import logging
import requests
import SeleniumLibrary.errors
from ..basic.core import SitesCore
from ta_captcha_solver.ta_captcha_solver import TACaptchaSolver
from ta_captcha_solver.exceptions import NoCaptchaException
from datetime import date, datetime, timedelta
from .exceptions import CentralReachException, ScheduledMaintenance
import time
import os
import shutil
import contextlib
import pyotp
from retry import retry


class CentralReachCore(SitesCore):
    def __init__(
        self,
        login: str,
        password: str,
        auth_totp_key: str = "",
        captcha_api_key: str | tuple[str, str] = "",
        url: str = "https://members.centralreach.com/#login",
        start_date: date = date.today().replace(day=1),
        end_date: date = date.today(),
        timeout: int = 30,
        temp_folder: str = "",
        headless: bool = False,
        client_id: str = "",
        client_secret: str = "",
    ):
        """
        CentralReachCore object. Please Inheritance it.

        :param login: login for CentralReach site.
        :param password: password for CentralReach site.
        :param url: url for CentralReach site.
        :param otp_code: otp_code for CentralReach site.
        :param auth_totp_key: auth_totp_key for CentralReach site.
        :param captcha_api_key: api_key for captcha solver - can be just api_key itself or (provider, api_key) tuple.
        :param start_date: start_date for filters. The default value is first day of the month.
        :param end_date: end_date for filters. The default value is today.
        :param timeout: timeout for action. The default value is 30 seconds.
        :param temp_folder: Path to temp folder. The default value is temp/cr.
        """
        super().__init__(login, password, auth_totp_key, url, timeout, temp_folder, headless)
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.client_id = client_id
        self.client_secret = client_secret
        self._do_auth = bool(self.client_id) and bool(self.client_secret)
        if isinstance(captcha_api_key, str):
            captcha_provider = "captcha.guru"
            api_key = captcha_api_key
        else:
            captcha_provider = captcha_api_key[0]
            api_key = captcha_api_key[1]

        self.captcha_solver = TACaptchaSolver.get(
            captcha_type="v2",
            browser=self.browser,
            service_provider_name=captcha_provider,
            service_provider_key=api_key,
        )

    def _get_auth_token(self, client_id, client_secret):
        """Retrieve the authentication token."""
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "cr-api",
        }

        return requests.post("https://login.centralreach.com/connect/token", data=data)

    def _get_internal_cookie(self, jwt):
        """Exchange the authentication token for an internal session cookie."""
        import requests

        headers = {
            "Accept": "application/json",
        }

        json_data = {
            "token": jwt["access_token"],
        }

        return requests.post(
            "https://members.centralreach.com/api/?framework.authtoken", headers=headers, json=json_data
        )

    def login_to_site(self) -> bool:
        """
        Try login to the site.

        :return: Status of the login. True if successfully log in
        """
        username_field = '//*[@id="Username"]'
        next_btn = '//*[@id="login"]'
        password_field = '//*[@id="Password"]'

        self.is_site_available = False
        self.browser.close_browser()

        if self.temp_folder:
            if os.path.exists(self.temp_folder):
                shutil.rmtree(self.temp_folder)
            os.mkdir(self.temp_folder)
            self.browser.set_download_directory(self.temp_folder, True)

        for i in range(1, 4):
            try:
                self.browser.open_chrome_browser(self.url, headless=self._headless)

                # get API auth cookies for RPA automation
                if self._do_auth:
                    new_cookies = self._get_internal_cookie(
                        self._get_auth_token(self.client_id, self.client_secret).json()
                    )

                    for cookie_name, cookie_value in new_cookies.cookies.get_dict().items():
                        self.browser.add_cookie(str(cookie_name), str(cookie_value))

                self.browser.set_window_size(1920, 1080)
                self.wait_element(username_field, is_need_screenshot=False, timeout=10)

                self.check_scheduled_maintenance()

                self.wait_element(username_field)
                self.browser.input_text_when_element_is_visible(username_field, self.login)
                self.browser.click_button_when_visible(next_btn)

                self.wait_element(password_field)
                self.browser.input_text_when_element_is_visible(password_field, self.password)

                for attempt in range(1, 4):
                    try:
                        with contextlib.suppress(NoCaptchaException):
                            self.captcha_solver.solve()
                        self.browser.click_button_when_visible(next_btn)
                        logging.info("Successfully Bypassed Captcha")
                        break
                    except Exception as ex:
                        logging.error(f"Failed to Bypass Captcha Attempt: {attempt}")
                        self.browser.capture_page_screenshot(
                            os.path.join(self.output_folder, f"Captcha_failed_Attempt_{attempt}.png")
                        )
                        if attempt == 3:
                            raise ex
                        continue

                self.is_password_expired = self.check_password_expired()
                if self.is_password_expired:
                    break

                if self.browser.does_page_contain_element(
                    '//div[@class="loginError"]/div[text()="There was an unexpected problem signing in. If you keep seeing this, please contact CentralReach Support"]'  # noqa
                ):
                    elem = self.browser.find_element(
                        '//div[@class="loginError"]/div[text()="There was an unexpected problem signing in. If you keep seeing this, please contact CentralReach Support"]'  # noqa
                    )
                    if elem.is_displayed():
                        logging.warning("Logging into CentralReach failed. There was an unexpected problem signing in.")
                        raise CentralReachException(
                            "Unexpected error during signing in. If you keep seeing this, contact CentralReach Support"
                        )

                self.pass_mfa()
                self.wait_element_and_refresh('//span[text()="Favorites"]', is_need_screenshot=False)

                if self.does_element_displayed('//span[text()="Continue To Login"]'):
                    self.click('//span[text()="Continue To Login"]')

                self.is_site_available = self.browser.does_page_contain_element('//span[text()="Favorites"]')
                self.base_url: str = self.get_base_url(self.browser.get_location())

                return self.is_site_available
            except ScheduledMaintenance as ex:
                raise ex
            except Exception as ex:
                logging.error(f"Logging into CentralReach. Attempt #{i} failed")
                logging.error(str(ex))
                self.browser.capture_page_screenshot(os.path.join(self.output_folder, f"Login_failed_Attempt_{i}.png"))
                self.browser.close_browser()
        return False

    def wait_element(self, xpath: str, timeout: int = 60, is_need_screenshot: bool = True) -> bool:
        """
        Wait element some time.

        :param xpath: Xpath of the element
        :param timeout: How long to wait if the item does not appear?
        :param is_need_screenshot: Do need to take a screenshot?
        :return: True if element found, else False
        """
        is_success: bool = False
        timer: datetime = datetime.now() + timedelta(seconds=timeout)

        while not is_success and timer > datetime.now():
            self.__close_specific_windows('//button[contains(@id, "pendo-close-guide")]')
            self.__close_specific_windows('//button[text()="Okay, got it!"]')
            self.__close_specific_windows('//button[text()="Remind Me Later"]')
            self.__close_specific_windows('//button[text()="REGISTER NOW"]')

            self.check_scheduled_maintenance()

            if self.browser.does_page_contain_element(xpath):
                try:
                    is_success = self.browser.find_element(xpath).is_displayed()
                except Exception:
                    time.sleep(1)

            if not is_success:
                if self.browser.does_page_contain_element(
                    "//div[@id='select2-drop']/ul[@class='select2-results']/li[@class='select2-no-results']"
                ):
                    elem = self.browser.find_element(
                        "//div[@id='select2-drop']/ul[@class='select2-results']/li[@class='select2-no-results']"
                    )
                    if elem.is_displayed():
                        break
        if not is_success and is_need_screenshot:
            now: datetime = datetime.now()
            logging.warning(f'[{now.strftime("%H:%M:%S")}] Element \'{xpath}\' not available')
            self.browser.capture_page_screenshot(
                os.path.join(self.output_folder, f'Element_not_available_{now.strftime("%H_%M_%S")}.png')
            )
        return is_success

    def __close_specific_windows(self, xpath: str) -> None:
        if self.browser.does_page_contain_element(xpath):
            for i in range(5):
                try:
                    elements: list = self.browser.find_elements(xpath)
                    for element in elements:
                        try:
                            if element.is_displayed():
                                logging.warning(
                                    "A pop-up appeared and the bot closed it. "
                                    "Please validate the screenshot in the artifacts."
                                )
                                self.browser.capture_page_screenshot(
                                    os.path.join(
                                        self.output_folder, f'Pop_up_{datetime.now().strftime("%H_%M_%S")}.png'
                                    )
                                )
                                element.click()
                                self.browser.wait_until_element_is_not_visible(
                                    f"({xpath})[{elements.index(element) + 1}]"
                                )
                        except (AssertionError, SeleniumLibrary.errors.ElementNotFound):
                            time.sleep(1)
                    return None
                except Exception as ex:
                    logging.warning(ex)

    def check_scheduled_maintenance(self):
        if self.browser.does_page_contain_element("//div[contains(text(),'We’ll Be Back Soon')]"):
            if self.browser.find_element("//div[contains(text(),'We’ll Be Back Soon')]").is_displayed():
                self.browser.capture_page_screenshot(
                    os.path.join(self.output_folder, f'Maintenance_{datetime.now().strftime("%H_%M_%S")}.png')
                )
                raise ScheduledMaintenance(
                    "Data processing stopped due to Scheduled Maintenance. "
                    "Please run the bot again when the CentralReach is available"
                )

    def wait_element_and_refresh(self, xpath: str, timeout: int = 120, is_need_screenshot: bool = True) -> bool:
        """
        Wait element some time and refresh page.

        :param xpath: Xpath of the element
        :param timeout: How long to wait if the item does not appear?
        :param is_need_screenshot: Do need to take a screenshot?
        :return: True if element found, else False
        """
        is_success: bool = False
        timer: datetime = datetime.now() + timedelta(seconds=timeout)

        while not is_success and timer > datetime.now():
            is_success = self.wait_element(xpath, 45, False)
            if not is_success:
                self.browser.reload_page()
        if not is_success and is_need_screenshot:
            now: datetime = datetime.now()
            logging.warning(f'[{now.strftime("%H:%M:%S")}] Element \'{xpath}\' not available')
            self.browser.capture_page_screenshot(
                os.path.join(self.output_folder, f'Element_not_available_{now.strftime("%H_%M_%S")}.png')
            )
        return is_success

    def apply_filter(self, filter_name: str, additional_params: str = "", is_need_wait: bool = True):
        if self.browser.does_page_contain_element('//li/a[@data-click="openMenu"]'):
            if self.browser.find_element('//li/a[@data-click="openMenu"]').is_displayed():
                self.click('//li/a[@data-click="openMenu"]')

        self.wait_element("//li/a[text()='Filters']")
        self.browser.click_element_when_visible("//li/a[text()='Filters']")

        self.wait_element("//a/span[text()='Saved filters']")
        if self.browser.does_page_contain_element("//a/span[text()='" + filter_name + "']"):
            if not self.browser.find_element("//a/span[text()='" + filter_name + "']").is_displayed():
                self.browser.click_element_when_visible("//a/span[text()='Saved filters']")
        else:
            self.browser.click_element_when_visible("//a/span[text()='Saved filters']")
        self.wait_element("//a/span[text()='" + filter_name + "']")
        self.browser.click_element_when_visible("//a/span[text()='" + filter_name + "']")
        self.wait_element("//li[contains(@class, 'filter-highlight')]")

        # Update filters value
        if additional_params:
            updated_url: str = self.browser.get_location()
            updated_url += additional_params
            self.browser.go_to(updated_url)

        if is_need_wait:
            self.browser.wait_until_element_is_not_visible("//em[contains(., '<loading>')]", timedelta(seconds=45))
            self.browser.wait_until_element_is_not_visible(
                "//div[contains(@data-bind, 'loading()')]", timedelta(seconds=45)
            )

    def is_no_results(self) -> bool:
        self.wait_element(
            '//div[text()="No results matched your keywords, filters, or date range" and not(@style="display: none;")]',
            5,
            False,
        )
        if self.browser.does_page_contain_element(
            '//div[text()="No results matched your keywords, filters, or date range" and not(@style="display: none;")]'
        ):
            return True
        return False

    def apply_label(self, label_add: str, label_remove: str = "") -> None:
        self.wait_element('//button[contains(., "Label selected")]')
        self.browser.click_element_when_visible('//button[contains(., "Label selected")]')

        if label_add:
            self.wait_element('//h4[text()="Apply Labels"]/../../div/div/ul/li/input')
            self.browser.input_text('//h4[text()="Apply Labels"]/../../div/div/ul/li/input', label_add)
            self.wait_element(f'//div[text()="{label_add}" and @role="option"]')
            if self.browser.does_page_contain_element(
                "//div[@id='select2-drop']/ul[@class='select2-results']/li[@class='select2-no-results']"
            ):
                self.browser.input_text('//h4[text()="Apply Labels"]/../../div/div/ul/li/input', label_add.lower())
                self.wait_element(f'//div[text()="{label_add}" and @role="option"]')
            self.browser.click_element_when_visible(f'//div[text()="{label_add}" and @role="option"]')
        if label_remove:
            self.wait_element('//h4[text()="Remove Labels"]/../../div/div/ul/li/input')
            self.browser.input_text('//h4[text()="Remove Labels"]/../../div/div/ul/li/input', label_remove)
            self.wait_element(f'//div[text()="{label_remove}" and @role="option"]')
            if self.browser.does_page_contain_element(
                "//div[@id='select2-drop']/ul[@class='select2-results']/li[@class='select2-no-results']"
            ):
                self.browser.input_text('//h4[text()="Remove Labels"]/../../div/div/ul/li/input', label_remove.lower())
                self.wait_element(f'//div[text()="{label_remove}" and @role="option"]')
            self.browser.click_element_when_visible(f'//div[text()="{label_remove}" and @role="option"]')

        self.browser.click_element_when_visible('//button[text()="Apply Label Changes"]')
        self.browser.wait_until_element_is_not_visible('//button[text()="Apply Label Changes"]')
        self.browser.wait_until_element_is_not_visible('//h2[text()="Bulk Apply Labels"]')

    def change_billing(self, column_name: str, billing: str):
        self.browser.click_element_when_visible(
            '//th[contains(.,"'
            + column_name
            + '")]/div/a[contains(@data-bind, "{title: \'Search for different provider\'}")]'
        )

        self.wait_element('//th[contains(.,"{column_name}")]/div/div/input')
        self.browser.input_text_when_element_is_visible(f'//th[contains(.,"{column_name}")]/div/div/input', billing)

        self.wait_element(f'//li/div[contains(.,"{billing}")]', timeout=10)
        if self.browser.does_page_contain_element(f'//li/div[contains(.,"{billing}")]'):
            self.browser.click_element_when_visible(f'//li/div[contains(.,"{billing}")]')
        self.sync_to_all_claims(column_name)

    def select_timesheets(self, timesheets_id: list) -> None:
        for timesheet_id in timesheets_id:
            self.browser.scroll_element_into_view(f'//tr[@id="billing-grid-row-{timesheet_id}"]/td/input')
            self.browser.select_checkbox(f'//tr[@id="billing-grid-row-{timesheet_id}"]/td/input')

    def unselect_timesheets(self, timesheets_id: list) -> None:
        for timesheet_id in timesheets_id:
            self.browser.scroll_element_into_view(f'//tr[@id="billing-grid-row-{timesheet_id}"]/td/input')
            self.browser.unselect_checkbox(f'//tr[@id="billing-grid-row-{timesheet_id}"]/td/input')

    def clear_location(self):
        self.click_button_by_text("Facility", "Clear location")
        self.sync_to_all_claims("Facility")

    def clear_provider_supplier(self):
        self.click_button_by_text("Provider Supplier", "Clear provider supplier")
        self.sync_to_all_claims("Provider Supplier")

    def clear_referrer(self):
        self.click_button_by_text("Referrer", "Clear referrer")
        self.sync_to_all_claims("Referrer")

    def click_button_by_text(self, column_name: str, button_text: str):
        self.wait_element(f'//th[contains(.,"{column_name}")]/div/div/a/i')
        self.browser.click_element_when_visible(f'//th[contains(.,"{column_name}")]/div/div/a/i')
        self.wait_element(f'//th[contains(.,"{column_name}")]//a[text()="{button_text}"]')
        self.browser.click_element_when_visible(f'//th[contains(.,"{column_name}")]//a[text()="{button_text}"]')

    def sync_to_all_claims(self, column_name: str):
        self.wait_element(f'//th[contains(.,"{column_name}")]/div/div/a/i')
        self.browser.click_element_when_visible(f'//th[contains(.,"{column_name}")]/div/div/a/i')
        self.wait_element(f'//th[contains(.,"{column_name}")]//a[text()="To all claims"]')
        self.browser.click_element_when_visible(f'//th[contains(.,"{column_name}")]//a[text()="To all claims"]')

    def click_action_and_bulk_merge_claims(self) -> None:
        self.wait_element('//a[contains(., "Action")]')
        self.browser.click_element_when_visible('//a[contains(., "Action")]')

        self.wait_element('//a[contains(., "Bulk-merge Claims")]')
        self.browser.click_element_when_visible('//a[contains(., "Bulk-merge Claims")]')

    def check_and_update_billing(self, valid_billing: str, full_billing_name: str):
        all_billings = self.browser.find_elements('//a[contains(@data-bind, "billingName")]')
        for billing in all_billings:
            if valid_billing.lower() not in str(billing.text).lower():
                self.change_billing("Billing", full_billing_name)
                break

    def check_password_expired(self):
        with contextlib.suppress(AssertionError):
            self.browser.wait_until_element_is_visible("//*[contains(text(), 'Your password has expired')]", 10)
            logging.info("Please reset AI worker password for Central Reach")
            return True
        return False

    def reset_password(self, new_password):
        self.wait_element('//input[@id="NewPassword"]')
        self.browser.input_text_when_element_is_visible('//input[@id="NewPassword"]', self.login)

        self.wait_element('//input[@id="ConfirmNewPassword"]')
        self.browser.input_text_when_element_is_visible('//input[@id="ConfirmNewPassword"]', self.login)

        self.wait_element('//button[@data-testid="update-password"]')
        self.browser.click_element_when_visible('//button[@data-testid="update-password"]')

        self.browser.close_all_browsers()

    @retry(tries=3, delay=10)
    def pass_mfa(self):
        if not self.browser.is_element_visible('//*[@id="verify-code"]'):
            return
        if str(self.auth_totp_key):
            try:
                base32_key = self.auth_totp_key.replace(" ", "").upper()
                totp = pyotp.TOTP(base32_key)
                otp_code = totp.now()
                self.wait_element('//*[@id="Code"]')
                self.browser.input_text('//*[@id="Code"]', otp_code, clear=True)
                self.browser.click_button_when_visible('//*[@id="verify-code"]')
                time.sleep(5)
                if self.browser.is_element_visible('//*[contains(text(),"Invalid code")]'):
                    raise CentralReachException("Invalid MFA code")
                self.browser.wait_until_element_is_not_visible('//*[@id="Code"]')
            except Exception as ex:
                raise CentralReachException(f"Error during MFA: {str(ex)}")
        else:
            raise CentralReachException("Auth Key is not provided")

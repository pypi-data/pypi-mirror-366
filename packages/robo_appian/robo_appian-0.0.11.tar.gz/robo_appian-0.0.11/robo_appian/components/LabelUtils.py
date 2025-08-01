from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LabelUtils:
    """
    Utility class for interacting with label components in Appian UI.

        Usage Example:

        # Find a label component
        from robo_appian.components.LabelUtils import LabelUtils
        label_component = LabelUtils.find(wait, "Username")

    """

    @staticmethod
    def find(wait: WebDriverWait, label: str):
        """
        Finds a label component by its text.

        Parameters:
            wait: Selenium WebDriverWait instance.
            label: The visible text label of the component.

        Returns:
            The Selenium WebElement for the label component.

        Example:
            LabelUtils.find(wait, "Username")

        """
        # This method locates a label component that contains the specified text.
        # It uses XPath to find the element that matches the text.

        xpath = f".//*[normalize-space(text())='{label}']"
        try:
            component = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutError as e:
            raise TimeoutError(
                f"Label '{label}' not found within the timeout period."
            ) from e
        except Exception as e:
            raise Exception(
                f"Label '{label}' not found within the timeout period."
            ) from e

        return component

    @staticmethod
    def click(wait: WebDriverWait, label: str):
        component = LabelUtils.find(wait, label)
        component.click()

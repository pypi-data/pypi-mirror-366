from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class TabUtils:
    """
    Utility class for interacting with tab components in Appian UI.

    Usage Example:

        # Select a tab by its label
        from robo_appian.components.TabUtils import TabUtils
        TabUtils.selectInactiveTab(wait, "Settings")

        # Find the currently selected tab by its label
        from robo_appian.components.TabUtils import TabUtils
        selected_tab = TabUtils.findSelectedTab(wait, "Settings")
    """

    @staticmethod
    def findSelectedTab(wait, label):
        """
        Finds the currently selected tab by its label.

        Parameters:
        wait: Selenium WebDriverWait instance.
            label: The visible text label of the tab.

        Returns:
            The Selenium WebElement for the selected tab.

        Example:
            TabUtils.findSelectedTab(wait, "Settings")
        """
        # This method locates a tab that is currently selected and contains the specified label.

        xpath = f".//div[./div[./div/div/div/div/div/p/strong[normalize-space(text())='{label}']]/span[text()='Selected Tab.']]/div[@role='link']"
        try:
            component = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutError as e:
            raise TimeoutError(f"Could not find selected tab with label '{label}': {e}")
        except Exception as e:
            raise RuntimeError(f"Could not find selected tab with label '{label}': {e}")
        return component

    @staticmethod
    def selectInactiveTab(wait, label):
        """
        Selects a tab by its label.

        Parameters:
            wait: Selenium WebDriverWait instance.
            label: The visible text label of the tab to select.

        Example:
            TabUtils.selectInactiveTab(wait, "Settings")
        """
        # This method locates a tab that contains a label with the specified text.

        xpath = f".//div[@role='link']/div/div/div/div/div[./p/span[text()='{label}']]"
        # xpath=f".//div[./div[./div/div/div/div/div/p/strong[normalize-space(text())='{label}']]/span[text()='Selected Tab.']]/div[@role='link']"
        try:
            component = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutError as e:
            raise TimeoutError(f"Could not find tab with label '{label}': {e}")
        except Exception as e:
            raise RuntimeError(f"Could not find tab with label '{label}': {e}")
        component.click()

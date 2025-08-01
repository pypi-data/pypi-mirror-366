from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TableUtils:
    """
    Utility class for interacting with table components in Appian UI.

        Usage Example:

        # Find a table using a column name
        from robo_appian.components.TableUtils import TableUtils
        table = TableUtils.findTableByColumnName(wait, "Status")

    """

    @staticmethod
    def findTableByColumnName(wait: WebDriverWait, columnName: str):
        """
        Finds a table component that contains a column with the specified name.

        Parameters:
            wait: Selenium WebDriverWait instance.
            columnName: The name of the column to search for in the table.

        Returns:
            The Selenium WebElement for the table component.

        Example:
            table = TableUtils.findTableByColumnName(wait, "Status")

        """
        # This method locates a table that contains a header cell with the specified column name.
        # It uses XPath to find the table element that has a header cell with the specified 'columnName'.
        # The 'abbr' attribute is used to match the column name, which is a common practice in Appian UI tables.

        # xpath = f".//table[./thead/tr/th[@abbr='{columnName}']]"
        xpath = f'.//table[./thead/tr/th[@abbr="{columnName}"]]'
        try:
            component = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutError as e:
            raise TimeoutError(
                f"Could not find table with column name '{columnName}': {e}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Could not find table with column name '{columnName}': {e}"
            )
        return component

    @staticmethod
    def rowCount(tableObject):
        """
        Returns the number of rows in a table, excluding empty grid messages.

        Parameters:
            tableObject: The Selenium WebElement representing the table.

        Returns:
            The number of rows in the table.

        Example:
            count = TableUtils.rowCount(table)

        """
        # This method counts the number of rows in a table by finding all the table row elements
        # that do not have the 'data-empty-grid-message' attribute.

        xpath = "./tbody/tr[./td[not (@data-empty-grid-message)]]"
        rows = tableObject.find_elements(By.XPATH, xpath)
        return len(rows)

    @staticmethod
    def findColumNumberByColumnName(tableObject, columnName):
        """
        Finds the column number in a table based on the column name.

        Parameters:
            tableObject: The Selenium WebElement representing the table.
            columnName: The name of the column to find.

        Returns:
            The index of the column (0-based).

        Example:
            column_number = TableUtils.findColumNumberByColumnName(table, "Status")

        """
        # This method locates the column header cell with the specified column name
        # and extracts the column index from its class attribute.

        xpath = f'./thead/tr/th[@scope="col" and @abbr="{columnName}"]'
        component = tableObject.find_element(By.XPATH, xpath)

        if component is None:
            raise ValueError(
                f"Could not find a column with abbr '{columnName}' in the table header."
            )

        class_string = component.get_attribute("class")
        partial_string = "headCell_"
        words = class_string.split()
        selected_word = None

        for word in words:
            if partial_string in word:
                selected_word = word

        if selected_word is None:
            raise ValueError(
                f"Could not find a class containing '{partial_string}' in the column header for '{columnName}'."
            )

        data = selected_word.split("_")
        return int(data[1])

    @staticmethod
    def findComponentFromTableCell(wait, rowNumber, columnName):
        """
        Finds a component within a specific table cell based on the row number and column name.

        Parameters:
            wait: Selenium WebDriverWait instance.
            rowNumber: The row number (0-based index) where the component is located.
            columnName: The name of the column where the component is located.

        Returns:
            The Selenium WebElement for the component within the specified table cell.

        Example:
            component = TableUtils.findComponentFromTableCell(wait, 2, "Status")

        """
        # This method locates a specific component within a table cell based on the provided row number
        # and column name. It constructs an XPath that targets the table cell containing the specified column
        # and row, and then retrieves the component within that cell.

        tableObject = TableUtils.findTableByColumnName(wait, columnName)
        columnNumber = TableUtils.findColumNumberByColumnName(tableObject, columnName)
        # xpath=f'./tbody/tr[@data-dnd-name="row {rowNumber+1}"]/td[not (@data-empty-grid-message)][{columnNumber}]'
        # component = tableObject.find_elements(By.XPATH, xpath)
        rowNumber = rowNumber + 1
        columnNumber = columnNumber + 1
        xpath = f'.//table[./thead/tr/th[@abbr="{columnName}"]]/tbody/tr[@data-dnd-name="row {rowNumber}"]/td[not (@data-empty-grid-message)][{columnNumber}]/*'
        try:
            component = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutError as e:
            raise TimeoutError(
                f"Could not find component in cell at row {rowNumber}, column '{columnName}': {e}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Could not find component in cell at row {rowNumber}, column '{columnName}': {e}"
            )
        # childComponent=component.find_element(By.xpath("./*"))
        return component

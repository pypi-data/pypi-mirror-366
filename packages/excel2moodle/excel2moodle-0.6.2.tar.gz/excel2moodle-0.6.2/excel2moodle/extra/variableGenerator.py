import logging
import random

from asteval import Interpreter
from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)

from excel2moodle.core.question import Parametrics
from excel2moodle.ui.UI_variableGenerator import Ui_VariableGeneratorDialog

logger = logging.getLogger(__name__)


class VariableGeneratorDialog(QDialog):
    def __init__(self, parent: QMainWindow, parametrics: Parametrics) -> None:
        super().__init__(parent)
        self.ui = Ui_VariableGeneratorDialog()
        self.ui.setupUi(self)
        self.origParametrics = parametrics
        self._generatedParametrics: Parametrics = Parametrics(
            parametrics.equations, parametrics._resultChecker, identifier="genr"
        )
        # Load existing rules
        for rule in self.origParametrics.variableRules:
            self.ui.listWidget_rules.addItem(rule)

        self._populate_variables_table()
        populateDataSetTable(
            self.ui.tableWidget_existing_variables,
            parametrics=self.origParametrics,
        )
        self._connect_signals()

        # Initially hide the existing variables table and generated variables table
        self.ui.tableWidget_existing_variables.hide()
        self.ui.groupBox_generated_variables.hide()

        self.aeval = Interpreter(minimal=True)  # Initialize asteval interpreter

    def _populate_variables_table(self) -> None:
        self.ui.tableWidget_variables.setRowCount(len(self.origParametrics.variables))
        for row, (var_name, values) in enumerate(
            self.origParametrics.variables.items()
        ):
            self.ui.tableWidget_variables.setItem(row, 0, QTableWidgetItem(var_name))
            # Add QLineEdit for Min, Max, and Decimal Places
            min_le = QLineEdit(str(min(values)) if values else "0")
            max_le = QLineEdit(str(max(values)) if values else "100")
            dec_le = QLineEdit("0")  # Default to 0 decimal places

            self.ui.tableWidget_variables.setCellWidget(row, 1, min_le)
            self.ui.tableWidget_variables.setCellWidget(row, 2, max_le)
            self.ui.tableWidget_variables.setCellWidget(row, 3, dec_le)

    def _connect_signals(self) -> None:
        self.ui.pushButton_addRule.clicked.connect(self._add_rule)
        self.ui.pushButton_removeRule.clicked.connect(self._remove_rule)
        self.ui.pushButton_generate.clicked.connect(self.generateSets)
        self.ui.pushButton_cancel.clicked.connect(self.reject)
        self.ui.pushButton_save.clicked.connect(self._save_variables_and_close)
        self.ui.groupBox_existing_variables.toggled.connect(
            self.ui.tableWidget_existing_variables.setVisible
        )

    def _add_rule(self) -> None:
        rule_text = self.ui.lineEdit_newRule.text().strip()
        if rule_text:
            self.ui.listWidget_rules.addItem(rule_text)
            self.ui.lineEdit_newRule.clear()

    def _remove_rule(self) -> None:
        for item in self.ui.listWidget_rules.selectedItems():
            self.ui.listWidget_rules.takeItem(self.ui.listWidget_rules.row(item))

    def generateSets(self) -> None:
        self._generatedParametrics.resetVariables()  # Clear previous generated sets
        self._rule_error_occurred = False  # Reset error flag

        varConstraints = {}
        for row in range(self.ui.tableWidget_variables.rowCount()):
            var_name = self.ui.tableWidget_variables.item(row, 0).text()
            varConstraints[var_name] = {
                "min": float(self.ui.tableWidget_variables.cellWidget(row, 1).text()),
                "max": float(self.ui.tableWidget_variables.cellWidget(row, 2).text()),
                "decimal_places": int(
                    self.ui.tableWidget_variables.cellWidget(row, 3).text()
                ),
            }

        rules = [
            self.ui.listWidget_rules.item(i).text()
            for i in range(self.ui.listWidget_rules.count())
        ]

        num_sets = self.ui.spinBox_numSets.value()

        try:
            generated_sets = [
                self._findSet(varConstraints, rules) for _ in range(num_sets)
            ]
        except IndexError as e:
            logger.exception("Invalid variables in Rule:")
            QMessageBox.critical(self, "Rule Error", f"{e}")
        except ValueError as e:
            logger.warning("No variable set found:")
            QMessageBox.warning(
                self,
                "Generation Failed",
                f"{e} Consider relaxing your rules or increasing the number of attempts.",
            )
        else:
            # convert the generated_sets list[dict[str, float]] into dict[str, list[float]]
            # [{A:7, B:8}, {A:11, B:9}] -> {A: [7, 11], B: [8, 9]}
            newVariables = {}
            for var in self.origParametrics.variables:
                newVariables[var] = [dataSet[var] for dataSet in generated_sets]
            self._generatedParametrics.variables = newVariables
            self.ui.groupBox_generated_variables.show()
            populateDataSetTable(
                self.ui.tableWidget_generated_variables,
                parametrics=self._generatedParametrics,
            )

    def _findSet(
        self,
        constraints: dict[str, dict[str, float | int]],
        rules: list[str],
        maxAttempts: int = 1000,
    ) -> dict[str, float]:
        """Generate Random numbers for each variable and check if the rules apply.

        Raises
        ------
            `IndexError`: if the evaluation of the rule returns `None`
            `ValueError`: if fater `maxAttemps` no set is found

        """
        attempts = 0
        while attempts < maxAttempts:
            current_set: dict[str, float] = {}
            # Generate initial values based on min/max constraints
            for var_name, constr in constraints.items():
                min_val: float = constr["min"]
                max_val: float = constr["max"]
                dec_places: int = constr["decimal_places"]

                if dec_places == 0:
                    current_set[var_name] = float(
                        random.randint(int(min_val), int(max_val))
                    )
                else:
                    current_set[var_name] = round(
                        random.uniform(min_val, max_val), dec_places
                    )
            if self._check_rules(current_set, rules):
                logger.info("Found matching set after %s attemps", attempts)
                return current_set
            attempts += 1
        msg = f"Could not generate a valid set after {maxAttempts} attempts."
        raise ValueError(msg)

    def _check_rules(
        self, varSet: dict[str, float], rules: list[str], show_error: bool = True
    ) -> bool:
        # Create a local scope for evaluating rules
        self.aeval.symtable.update(varSet)

        for rule in rules:
            # Evaluate the rule using asteval
            res = self.aeval(rule)
            if res is None:
                msg = f"Error evaluating rule '{rule}'"
                raise IndexError(msg)
            if res is False:
                return False
        return True

    def _save_variables_and_close(self) -> None:
        """Format variables set to fit `Parametrics`."""
        logger.info("Saving new variables to the question")
        newVars = self.origParametrics.variables.copy()
        for varName in newVars:
            newVars[varName].extend(self._generatedParametrics.variables[varName])
        self.origParametrics.variableRules = [
            self.ui.listWidget_rules.item(i).text()
            for i in range(self.ui.listWidget_rules.count())
        ]
        self.origParametrics.variables = newVars
        logger.info("Rules saved to Parametrics.")
        self.accept()


def populateDataSetTable(
    tableWidget: QTableWidget,
    parametrics: Parametrics | None = None,
) -> None:
    """Insert all Variables with their values into `tableWidget`."""
    if parametrics is None:
        return
    variables = parametrics.variables
    variants = parametrics.variants
    tableWidget.setRowCount(len(variables) + len(parametrics.results))
    tableWidget.setColumnCount(variants + 1)  # Variable Name + Variants
    headers = ["Variable"] + [f"Set {i + 1}" for i in range(variants)]
    tableWidget.setHorizontalHeaderLabels(headers)
    for row, (var, values) in enumerate(variables.items()):
        tableWidget.setItem(row, 0, QTableWidgetItem(var))
        for col, value in enumerate(values):
            tableWidget.setItem(row, col + 1, QTableWidgetItem(str(value)))
    for row, results in parametrics.results.items():
        logger.debug("adding Results to the DataSetTable: %s", results)
        tableWidget.setItem(
            len(variables) + row - 1, 0, QTableWidgetItem(f"Results: {row}")
        )
        for variant, res in enumerate(results):
            tableWidget.setItem(
                len(variables) + row - 1,
                variant + 1,
                QTableWidgetItem(str(res)),
            )
    tableWidget.resizeColumnsToContents()


# This part is for testing the UI independently
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    # Mock ParametricQuestion for testing
    class MockParametricQuestion:
        def __init__(self) -> None:
            self.origParametrics.variables = {
                "a": [1.0, 2.0, 3.0],
                "b": [10, 20, 30],
                "c": [0.5, 1.5, 2.5],
            }

    app = QApplication(sys.argv)
    mock_question = MockParametricQuestion()
    dialog = VariableGeneratorDialog(paramQuestion=mock_question)
    if dialog.exec():
        print("Generated Sets:", dialog.generatedVarSets())
    sys.exit(app.exec())

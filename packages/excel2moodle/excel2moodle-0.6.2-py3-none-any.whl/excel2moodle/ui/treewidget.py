"""The `treewidget` Module provides the `QuestionItem` and the `CategoryItem` item.

Those two are subclasses of `QTreeWidgetItem`, to provide an easy interface
of accessing the corresponding questions from the items.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem

from excel2moodle.core.dataStructure import Category
from excel2moodle.core.question import ParametricQuestion, Question


class QuestionItem(QTreeWidgetItem):
    def __init__(self, parent, question: Question | ParametricQuestion) -> None:
        super().__init__(parent)
        self.setData(2, Qt.UserRole, question)
        self.setText(0, question.id)
        self.setText(1, question.name)
        self.setText(2, str(question.points))
        if hasattr(question, "variants") and question.variants is not None:
            self.setText(3, str(question.variants))

    def getQuestion(self) -> Question | ParametricQuestion:
        """Return the question Object the QTreeWidgetItem represents."""
        return self.data(2, Qt.UserRole)


class CategoryItem(QTreeWidgetItem):
    def __init__(self, parent, category: Category) -> None:
        super().__init__(parent)
        self.setData(2, Qt.UserRole, category)
        self.setText(0, category.NAME)
        self.setText(1, category.desc)
        self.setText(2, str(category.points))
        var = self.getMaxVariants()
        if var != 0:
            self.setText(3, str(var))

    def iterateChildren(self):
        for child in range(self.childCount()):
            yield self.child(child)

    def getMaxVariants(self) -> int:
        count: int = 0
        for child in self.iterateChildren():
            q = child.getQuestion()
            if hasattr(q, "variants") and q.variants is not None:
                count = max(q.variants, count)
        return count

    def getCategory(self) -> Category:
        return self.data(2, Qt.UserRole)

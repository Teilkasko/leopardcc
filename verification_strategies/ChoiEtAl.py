from interfaces.VerificationStrategyInterface import VerificationStrategyInterface
from helpers.LizardHelper import compute_cyclomatic_complexity, is_new_function_improved, get_functions_sorted_by_complexity, measure_code_cc
from util.Logger import get_logger
from interfaces.NotImprovableException import NotImprovableException


class ChoiEtAl(VerificationStrategyInterface):
    """Verification methods adapted to JavaScript, taken from Choi, Jinsu et al. 2024: 'Iterative Refactoring of Real-World Open-Source Programs with Large Language Models'"""

    def verify_linting(self, function):
        lint_errors = function.project.get_lint_errors()
        does_linting_pass = len(lint_errors) == 0

        if not does_linting_pass:
            get_logger().info("Linting does not pass, attempting to fix")
            function.refactor_with_lint_errors(lint_errors)

            lint_errors = function.project.get_lint_errors()
            does_linting_pass = len(lint_errors) == 0
            if not does_linting_pass:
                raise NotImprovableException(function, "linting")

    def verify_unit_tests(self, function):
        test_errors = function.project.get_test_errors()
        do_tests_pass = len(test_errors) == 0

        if not do_tests_pass:
            get_logger().info("Unit tests do not pass, attempting to fix")
            function.refactor_with_test_errors(test_errors)
            self.verify_linting(function)

            test_errors = function.project.get_test_errors()
            do_tests_pass = len(test_errors) == 0
            if not do_tests_pass:
                raise NotImprovableException(function, "unit tests")

    def verify_improvement(self, function, functions_to_ignore):
        new_cc = measure_code_cc(function.current_code_in_dirty)
        is_improved = new_cc < function.old_cc

        if not is_improved:
            get_logger().info("Improvement is not satisfying, attempting to fix")
            function.refactor_for_better_improvement()
            self.verify_linting(function)
            self.verify_unit_tests(function)

            new_cc = measure_code_cc(function.current_code_in_dirty)
            is_improved = new_cc < function.old_cc
            if not is_improved:
                raise NotImprovableException(function, "complexity reduction")

        function.new_cc = new_cc

import json
import re
import os
import subprocess
from interfaces.LintError import LintError
from interfaces.TestError import TestError


def fix_eslint_issues(code: str, dirty_path: str) -> str:
    patch_file_path = dirty_path + "/patch.js"
    with open(patch_file_path, 'w') as patch_file:
        patch_file.write(code)
    
    lint_fix_command = 'cat patch.js | npx eslint --stdin --format json --fix-dry-run'
    proc = subprocess.run(['cd ' + dirty_path + ' && ' + lint_fix_command],
                        shell=True, capture_output=True, text=True, check=False)

    os.remove(patch_file_path) 
    
    linter_output = json.loads(proc.stdout)
    if 'output' in linter_output[0]:
        improved_code = linter_output[0]['output']
        return improved_code
    
    return code


def __get_eslint_errors_from_json_output(output: bytes | str) -> list[LintError]:
    lint_info = json.loads(output)
    errors: list[LintError] = []
    for file_object in lint_info:
        for message in file_object['messages']:
            file_path = file_object['filePath']
            target_line = message['line']
            with open(file_path, 'r') as code_file:
                content = code_file.readlines()
            erroneous_code = content[target_line - 1]

            error: LintError = {
                'rule_id': message['ruleId'],
                'message': message['message'],
                'file': file_path,
                'target_line': target_line,
                'erroneous_code': erroneous_code
            }
            errors.append(error)

    return errors


def get_eslint_errors(dirty_path: str, lint_command: str) -> list[LintError]:
    try: 
        eslint_json_name = 'eslint-output.json'
        output_options = ' --format json -o ' + eslint_json_name
        lint_command += output_options
        
        eslint_json_output_path = dirty_path + '/' + eslint_json_name

        subprocess.run(['cd ' + dirty_path + ' && ' + lint_command],
                        shell=True, capture_output=True, text=True, check=True, timeout=30)
        
        if os.path.exists(eslint_json_output_path):
            os.remove(eslint_json_output_path) 
        return []


    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        with open(eslint_json_output_path, 'r') as eslint_json_file:
            eslint_json_output = eslint_json_file.read()

        errors = __get_eslint_errors_from_json_output(eslint_json_output)

        if os.path.exists(eslint_json_output_path):
            os.remove(eslint_json_output_path) 
        return errors


def __get_mocha_errors_from_json_output(stdout: bytes | str, line_pattern: str) -> list[TestError]:
    test_info = json.loads(stdout)
    failures = test_info['failures']

    errors: list[TestError] = []
    for failure in failures:
        error: TestError = {'expectation': failure['fullTitle'],
                            'message_stack': failure['err']['stack'],
                            'test_file': failure['file'],
                            'target_line': None}
        line_match = re.search(line_pattern, failure['err']['stack'])
        if line_match is not None:
            error['target_line'] = int(line_match.group(1))
        errors.append(error)

    return errors


def get_mocha_errors(dirty_path: str, test_command: str, line_pattern: str) -> list[TestError]:
    try:
        mocha_json_name = 'mocha-output.json'
        output_options = ' --reporter json --reporter-option output=' + mocha_json_name
        test_command += output_options
        
        mocha_json_output_path = dirty_path + '/' + mocha_json_name
        
        subprocess.run(['cd ' + dirty_path + ' && ' + test_command],
                        shell=True, capture_output=True, text=True, check=True, timeout=30)
        
        if os.path.exists(mocha_json_output_path):
            os.remove(mocha_json_output_path) 
        return []

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        with open(mocha_json_output_path, 'r') as mocha_json_file:
            mocha_json_output = mocha_json_file.read()

        errors = __get_mocha_errors_from_json_output(mocha_json_output, line_pattern)

        if os.path.exists(mocha_json_output_path):
            os.remove(mocha_json_output_path) 
        return errors
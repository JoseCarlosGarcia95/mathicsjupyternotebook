#!//usr/bin/python
import json
import re
from ipykernel.kernelbase import Kernel

from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation, Message, Result, Output

class MathicsNotebookKernel(Kernel):
    implementation = 'mathics'
    implementation_version = '1.0'
    banner = 'Mathics Jupyter Kernel - Implementation'

    language_info = {
        'version': '1.0',
        'name': 'Mathematica',
        'mimetype': 'text/x-mathematica',
    }

    name = 'MathicsNotebook'
    
    """
    Handle jupyter connections.
    """
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        if not silent:
            from mathics.core.parser import MultiLineFeeder

            definitions = Definitions(add_builtin=True)
            evaluation  = Evaluation(definitions, format='xml')

            feeder = MultiLineFeeder(code, '<notebook>')
            results = []
            try:
                while not feeder.empty():
                    expr = evaluation.parse_feeder(feeder)
                    if expr is None:
                        results.append(Result(evaluation.out, None, None)) 
                        evaluation.out = []
                        continue
                    result = evaluation.evaluate(expr, timeout=20)
                    if result is not None:
                        results.append(result)
            except Exception as exc:
                raise

            for result in results:

                html = result.get_data()['result']
                html = re.sub(r"<math><mglyph width=\"(.*)\" height=\"(.*)\" src=\"(.*)\"/></math>", "<img width=\"\\1\" height=\"\\2\" src=\"\\3\" />", html, 0)
                
                display_data = {
                    'data' : {'text/html' : html},
                    'metadata' : {},
                }

                file = open('/var/tmp/debug_mathics.log', 'w+')
                file.write(json.dumps(result.get_data()))
                file.close()
       
                self.send_response(self.iopub_socket, 'display_data', display_data)

        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
        }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MathicsNotebookKernel)


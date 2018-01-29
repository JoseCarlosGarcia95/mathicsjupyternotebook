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
    Clear mathics output.
    """
    def clear_output(self, data):
        data = re.sub(r"<math><mglyph width=\"(.*)\" height=\"(.*)\" src=\"(.*)\"/></math>", "<img width=\"\\1\" height=\"\\2\" src=\"\\3\" />", data, 0)
        return data

    def read_static_file(self, static):
        static_file = file('/home/jose/Proyectos/mathicsjupyternotebook/web/' + static, 'r')
        content     = static_file.read()
        static_file.close()
        return content
    def initialize_javascript_if_needed(self):
        if self.execution_count == 1:
            inject_javascript_code = '<script type="text/javascript">'

            """
<script type="text/javascript" src="/media/js/prototype/prototype.js"></script>
<script type="text/javascript" src="/media/js/three/Three.js"></script>
<script type="text/javascript" src="/media/js/three/Detector.js"></script>

<script type="text/javascript" src="/media/js/mathjax/MathJax.js?config=MML_HTMLorMML&amp;delayStartupUntil=configured"></script>

<script type="text/javascript" src="/media/js/message.js"></script>
<script type="text/javascript" src="/media/js/authentication.js"></script>
<script type="text/javascript" src="/media/js/inout.js"></script>
<script type="text/javascript" src="/media/js/utils.js"></script>
<script type="text/javascript" src="/media/js/mathics.js"></script>
<script type="text/javascript" src="/media/js/graphics3d.js"></script>
<script type="text/javascript" src="/media/js/doc.js"></script>"""
            inject_javascript_code += self.read_static_file('media/js/prototype/prototype.js');
            inject_javascript_code += self.read_static_file('media/js/three/Three.js');
            inject_javascript_code += self.read_static_file('media/js/three/Detector.js');            
            inject_javascript_code += self.read_static_file('media/js/utils.js');            
            inject_javascript_code += self.read_static_file('media/js/mathics.js');            
            inject_javascript_code += self.read_static_file('media/js/graphics3d.js');            


            inject_javascript_code += '</script>'
            
            display_data = {
                'data' : {'text/html' : inject_javascript_code},
                'metadata' : {},
            }
            
            self.send_response(self.iopub_socket, 'display_data', display_data)
    """
    Handle jupyter connections.
    """
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        self.initialize_javascript_if_needed()
        
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
                result_data = result.get_data()
                
                result_html = self.clear_output(result_data['result'])
                
                display_data = {
                    'data' : {'text/html' : result_html},
                    'metadata' : {},
                }
       
                self.send_response(self.iopub_socket, 'display_data', display_data)

        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MathicsNotebookKernel)


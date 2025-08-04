
USER_CODE_ERROR = 'user_error'
SYSTEM_ERROR = 'system_error'
import logging
import traceback

class Skills:
    __instance = None

    def __init__(self):
        self._functions = {}
        self._rpc = None # remote procedure call

    @classmethod
    def _instance(cls, *args, **kwargs):
        if not Skills.__instance:
            Skills.__instance = Skills(*args, **kwargs)
        return Skills.__instance
    
    def _add_function(self, name, func):
        self._functions[name] = func

    def _remove_function(self, name):
        self._functions.pop(name, None)

    def _clear_functions(self):
        self._functions = {}

    def _get_function(self, name):
        return self._functions.get(name, None)
    
    def _update_rpc(self, rpc):
        self._rpc = rpc

    def _clear_rpc(self):
        self._rpc = None

    def _run(self, method, *args, **kwargs):
        func = self._get_function(method)
        if func:
            return func(*args, **kwargs)
        elif self._rpc is not None:
            result = self._rpc(method, *args, **kwargs)
            if isinstance(result, Exception):
                raise result
            else:
                return result
        else:
            raise ValueError(USER_CODE_ERROR, f'function {method} not found')

    def __getattr__(self, name):
        return Skills.Proxy(self, name)

    class Proxy:
        def __init__(self, instance, name):
            self.instance = instance
            self.chain = [name]

        def __getattr__(self, name):
            self.chain.append(name)
            return self

        def __call__(self, *args, **kwargs):
            try:
                full_name = '.'.join(self.chain)
                return self.instance._run(full_name, *args, **kwargs)
            except Exception as e:
                if isinstance(e, ValueError) and len(e.args) == 2 and e.args[0] == USER_CODE_ERROR:
                    error = e.args[1]
                    raise Exception(error) from None
                elif isinstance(e, ValueError) and len(e.args) == 2 and e.args[0] == SYSTEM_ERROR:
                    error = e.args[1]
                    logging.error(error)
                    raise ValueError(SYSTEM_ERROR, '平台发生错误，请稍后再试') from None
                else:
                    raise e from None
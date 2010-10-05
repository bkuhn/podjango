from mod_python import apache

# 404 should do NOTHING so apache can handle it.  This view is referenced
# in sflc.urls
def view404(request):
    from django.http import HttpResponseNotFound
    return HttpResponseNotFound("")

def outputfilter(filter):
    # set appropriate cache timeout
    filter.req.headers_out["Cache-Control"] = "max-age=600"

    # read raw template
    raw = []
    s = filter.read()
    while s:
        raw.append(s)
        s = filter.read()
    raw = "".join(raw)

    # render it
    from django.template import Context, Template
    t = Template(raw.decode('utf-8'))
    del raw
    cooked = t.render(Context())
    del t

    # send it off!
    filter.write(cooked.encode('utf-8'))
    if s is None:
        filter.close()

# This is unreferenced from this file, but it must be imported to
# enable template inheritance in the outputfilter!
import django.template.loader

# And now we override a few things in the module
# django.core.handlers.modpython

from django.core.handlers.modpython import *
del handler

class ModPythonRequest(ModPythonRequest):
    def is_secure(self):
        return self._req.get_options().has_key('HTTPS') and self._req.get_options()['HTTPS'] == 'on'

class ModPythonHandler(BaseHandler):
    request_class = ModPythonRequest

    def __call__(self, req):
        # mod_python fakes the environ, and thus doesn't process SetEnv.  This fixes that
        # (SFLC instance doesn't call this)
        #os.environ.update(req.subprocess_env)

        # now that the environ works we can see the correct settings, so imports
        # requesthat use settings now can work
        from django.conf import settings

        # if we need to set up middleware, now that settings works we can do it now.
        if self._request_middleware is None:
            self.load_middleware()

        set_script_prefix(req.get_options().get('django.root', '')) 
        signals.request_started.send(sender=self.__class__) 
        try:
            try:
                request = self.request_class(req)
            except UnicodeDecodeError:
                response = http.HttpResponseBadRequest()
            else:
                response = self.get_response(request)

                # Apply response middleware
                for middleware_method in self._response_middleware:
                    response = middleware_method(request, response)
                response = self.apply_response_fixes(request, response)
        finally:
            signals.request_finished.send(sender=self.__class__) 

        # SFLC: decline so apache can serve a static file
        if response.status_code == 404:
            return apache.DECLINED

        # Convert our custom HttpResponse object back into the mod_python req.
        req.content_type = response['Content-Type']
        for key, value in response.items():
            if key != 'content-type':
                req.headers_out[str(key)] = str(value)
        for c in response.cookies.values():
            req.headers_out.add('Set-Cookie', c.output(header=''))
        req.status = response.status_code
        try:
            for chunk in response:
                req.write(chunk)
        finally:
            response.close()

        return apache.DONE # skip all remaining phases (sf[l]c customization)

def postreadrequesthandler(req):
    # mod_python hooks into this function.
    return ModPythonHandler()(req)

# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import torndb
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

define("address", default="", help="run on the given address")
define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="localhost:3306", help="api database host")
define("mysql_database", default="dbname", help="api database name")
define("mysql_user", default="root", help="api database user")
define("mysql_password", default="password", help="api database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
        ]
        settings = dict(
            app_title=u"Service API",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            # static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="zV2.<+7w%k<htomk0MG0+40-Cacmg_KPh|[+-Xu(!99xi+e1,K&]|12 slc56L<o",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class TemplateRendering:
    """
    A simple class to hold methods for rendering templates.
    """
    def render_template(self, template_name, **kwargs):
        template_dirs = []
        if self.settings.get('template_path', ''):
            template_dirs.append(
                self.settings["template_path"]
            )

        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content


class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
    @property
    def db(self):
        return self.application.db

    def render_tpl(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        kwargs.update({
            'settings': self.settings,
            'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),
            'request': self.request,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
        })
        content = self.render_template(template_name, **kwargs)
        self.write(content)


class HomeHandler(BaseHandler):
    def get(self):
        return self.render_tpl('index.html');

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, options.address)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

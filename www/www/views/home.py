from pyramid.view import (
    view_config,
    view_defaults
)

from ..models import Contact
from ..tasks.contact import notify


@view_defaults(route_name='home', renderer='/home/home.jinja2')
class HomeViews:
    def __init__(self, request):
        # Used by the before_insert and before_update event listeners
        if request.user:
            request.dbsession.info['username'] = request.user.username
        self.request = request

    @view_config(route_name='home')
    def home(self):
        return {'page': 'home'}

    @view_config(route_name='landscapes', renderer='/home/landscapes.jinja2')
    def landscapes(self):
        return {'page': 'landscapes'}

    @view_config(route_name='family', renderer='/home/family.jinja2')
    def family(self):
        return {'page': 'family'}

    @view_config(route_name='about', renderer='/home/about.jinja2')
    def about(self):
        return {'page': 'about'}

    @view_config(route_name='contact', renderer='/home/contact.jinja2')
    def contact(self):
        email_sent = False

        if 'form.submitted' in self.request.params:
            roles = ['unauthenticated']
            to_email = self.request.site['contact']
            from_name = self.request.params['name']
            from_email = self.request.params['email']
            subject = self.request.params['subject']
            message = self.request.params['message']

            contact = Contact(roles=roles,
                              to_email=to_email,
                              from_name=from_name,
                              from_email=from_email,
                              subject=subject,
                              message=message)
            self.request.dbsession.add(contact)

            self.request.dbsession.flush()
            self.request.dbsession.refresh(contact)
            notify.delay(contact.id)
            email_sent = True

        return {
            'page': 'contact',
            'email_sent': email_sent,
            'url': self.request.route_url('contact'),
        }

    @view_config(route_name='faq', renderer='/home/faq.jinja2')
    def faq(self):
        return {'page': 'faq'}

import transaction
import smtplib

from email.message import EmailMessage
from sqlalchemy.orm.exc import NoResultFound

from www.celeryconf import app
from www.models.contact import Contact
from .sqlalchemytask import SqlAlchemyTask


# progress
# http://docs.celeryproject.org/en/latest/userguide/calling.html
@app.task(base=SqlAlchemyTask, bind=True, max_retries=10, default_retry_delay=10)
def notify(self, contact_id):
    if contact_id is None:
        return

    try:
        contact = self.dbsession.query(Contact).get(contact_id)

        if contact is None:
            raise NoResultFound

        msg = EmailMessage()
        msg['From'] = '"{}" <{}>'.format(contact.from_name, contact.from_email)
        msg['To'] = contact.to_email
        msg['Subject'] = contact.subject
        msg.set_content(contact.message)

        s = smtplib.SMTP('mailhog', 1025)
        s.send_message(msg)
        s.quit()
    except NoResultFound as exc:
        raise notify.retry(exc=exc)

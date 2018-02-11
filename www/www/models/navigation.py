from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, and_
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship, backref, load_only

from .meta import Base


class Navigation(Base):
    __tablename__ = 'navigation'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    modified_on = Column(DateTime(timezone=True), nullable=False)
    modified_by = Column(Text, ForeignKey('profile.username'), nullable=False)
    roles = Column(ARRAY(Text))
    parent_id = Column(Integer, ForeignKey("navigation.id"))
    menu_id = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False)
    page_title = Column(Text, nullable=False)
    route = Column(Text, nullable=False)
    params = Column(JSONB)
    created_by_user = relationship('Profile', foreign_keys=[created_by])
    modified_by_user = relationship('Profile', foreign_keys=[modified_by])
    children = relationship('Navigation',
                            backref=backref('parent', remote_side=[id]))

    def __repr__(self):
        return '<Navigation: {}>'.format(self.page_title)

    @classmethod
    def get_navigation(cls, session, menu_id):
        navigation = session.query(Navigation).filter(
            and_(Navigation.menu_id.like(menu_id), Navigation.parent_id == None)
            ).options(load_only('id', 'menu_id', 'page_title', 'route')
                      ).order_by(Navigation.sort_order).all()

        for nav in navigation:
            if nav.params is None:
                nav.params = {}

        return navigation

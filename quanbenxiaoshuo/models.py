from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()
engine = create_engine("mysql+pymysql://root:root@localhost:3306/quanben?charset=utf8", echo=False)
# echo表示将提示打印出老


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    created_time = Column(DateTime)
    book = relationship("Book", backref='category')

    def __str__(self):
        return "<Category '%s'>" % self.name


class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    href = Column(String(256))
    created_time = Column(DateTime)
    category_id = Column(Integer, ForeignKey('category.id'))

    def __str__(self):
        return "<Category '{}'>".format(self.name)


class Chapter(Base):
    __tablename__ = "chapter"
    id = Column(Integer, primary_key=True)
    href = Column(String(256))
    name = Column(String(256))
    chapter_text = Column(Text)
    book_id = Column(Integer, ForeignKey('book.id'))

    def __str__(self):
        return "<Chapter '{}'>".format(self.name)


Base.metadata.create_all(engine)
Session_class = sessionmaker(bind=engine)
"""
        | Book
category| Book  (One to Many)
        | Book
"""
from datetime import datetime
import os

from sqlalchemy import Column, create_engine, desc, Date, func, Integer, or_, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, StaticFileHandler, stream_request_body


class IndexHandler(RequestHandler):

    def initialize(self, SessionMaker):
        self.__SessionMaker = SessionMaker

    def get(self):
        session = self.__SessionMaker()
        recent_docs = session.query(DocModel).order_by(desc('date_uploaded')).limit(10)
        session.close()

        self.render('index.html', recent_docs=recent_docs)


class AddHandler(RequestHandler):

    def initialize(self, SessionMaker, stored_docs_path):
        self.__SessionMaker = SessionMaker
        self.__stored_docs_path = stored_docs_path

    def get(self):
        self.render('add.html')

    def post(self):
        new_doc = DocModel()

        # Get required arguments
        for each_property in ['doc_title', 'doc_description', 'source_org',
                'uploader_name', 'uploader_email']:

            value = self.get_argument(each_property)
            setattr(new_doc, each_property, value)

        # Make sure file contents are there
        file_array = self.request.files.get('file', None)

        if not file_array or len(file_array) == 0:
            self.set_status(400)
            self.write('Request missing file upload')
            return

        file_data = file_array[0]['body']
        filename = file_array[0]['filename']

        # Get optional fields
        tracking_number = self.get_argument('tracking_number', default=None)
        new_doc.tracking_number = tracking_number

        date_requested = self.get_argument('date_requested', default=None)
        if date_requested:
            date_requested = datetime.strptime(date_requested, '%m/%d/%Y').date()
        else:
            date_requested = None

        new_doc.date_requested = date_requested

        date_received = self.get_argument('date_received', default=None)
        if date_received:
            date_received = datetime.strptime(date_received, '%m/%d/%Y').date()
        else:
            date_received = None

        new_doc.date_received = date_received

        # Set metadata
        new_doc.date_uploaded = datetime.now().date()
        new_doc.filename = filename

        # Save document in sqlite to get id number
        session = self.__SessionMaker()
        session.add(new_doc)
        session.commit()

        document_id = new_doc.id
        session.close()

        # Use id number to write to disk
        file_path = os.path.join(self.__stored_docs_path, str(document_id), filename)

        os.mkdir(os.path.dirname(file_path))

        fd = open(file_path, 'w')
        fd.write(file_data)
        fd.close()

        self.write('Document added, thanks!')


class SearchHandler(RequestHandler):

    def initialize(self, SessionMaker):
        self.__SessionMaker = SessionMaker

    def get(self):
        query_arg = self.get_argument('query', default=None)
        offset = self.get_argument('offset', default=None)

        if not offset:
            offset = 0
        else:
            offset = int(offset)

        session = self.__SessionMaker()
        query = session.query(DocModel)

        if query_arg:
            query = query.filter(or_(
                DocModel.doc_title.like('%%%s%%' % query_arg),
                DocModel.doc_description.like('%%%s%%' % query_arg),
                DocModel.source_org.like('%%%s%%' % query_arg),
                DocModel.uploader_name.like('%%%s%%' % query_arg)
                ))
        else:
            query_arg = ''

        query = query.order_by(desc(DocModel.date_uploaded))

        count = query.count()

        matching_docs = query.offset(offset).limit(20).all()

        session.close()

        self.render(
            'search.html', query=query_arg, offset=offset, count=count,
            matching_docs=matching_docs
            )


class ViewHandler(RequestHandler):

    def initialize(self, SessionMaker):
        self.__SessionMaker = SessionMaker

    def get(self, document_id):
        session = self.__SessionMaker()
        doc = session.query(DocModel).filter(DocModel.id == document_id).one()
        session.close()

        self.render('view.html', doc=doc)


class DownloadHandler(RequestHandler):

    def initialize(self, stored_docs_path):
        self.__stored_docs_path = stored_docs_path

    def get(self, doc_id, filename):
        file_path = os.path.join(self.__stored_docs_path, str(doc_id), filename)

        if not os.path.exists(file_path):
            self.set_status(404)
            self.write('File not found')

        self.set_header('Content-Type', 'application/ocet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % filename)

        fd = open(file_path, 'r')

        while True:
            chunk = fd.read(1000000)

            if chunk:
                self.write(chunk)

            else:
                fd.close()
                break


class OrgHandler(RequestHandler):

    def initialize(self, SessionMaker):
        self.__SessionMaker = SessionMaker

    def get(self):
        session = self.__SessionMaker()

        org_results = session.query(
            DocModel.source_org, func.count(DocModel.source_org)).group_by(
                DocModel.source_org).order_by(DocModel.source_org).all()

        session.close()

        self.render('org.html', org_results=org_results)


class SubmitterHandler(RequestHandler):

    def initialize(self, SessionMaker):
        self.__SessionMaker = SessionMaker

    def get(self):
        session = self.__SessionMaker()

        submitter_results = session.query(
            DocModel.uploader_name, func.count(DocModel.uploader_name)).group_by(
                DocModel.uploader_name).order_by(DocModel.uploader_name).all()

        session.close()

        self.render('submitter.html', submitter_results=submitter_results)


Base = declarative_base()

class DocModel(Base):
    __tablename__ = 'docs'

    id = Column(Integer, primary_key=True)
    doc_title = Column(String)
    doc_description = Column(String)
    source_org = Column(String)
    tracking_number = Column(String, nullable=True)
    date_requested = Column(Date, nullable=True)
    date_received = Column(Date, nullable=True)
    uploader_name = Column(String)
    uploader_email = Column(String)
    filename = Column(String)
    date_uploaded = Column(Date)


if __name__ == '__main__':
    current_directory = os.path.dirname(__file__)
    static_path = os.path.join(current_directory, 'static')
    template_path = os.path.join(current_directory, 'templates')
    stored_docs_path = os.path.join(current_directory, 'storage', 'docs')

    engine = create_engine('sqlite:///storage/db/sqlite.db')
    Base.metadata.create_all(engine)
    SessionMaker = sessionmaker(engine)

    app = Application([
        (r'/static/(.*)', StaticFileHandler, {'path': static_path}),

        (r'/', IndexHandler, dict(SessionMaker=SessionMaker)),

        (r'/add', AddHandler, dict(
            SessionMaker=SessionMaker,
            stored_docs_path=stored_docs_path
            )),

        (r'/search', SearchHandler, dict(
            SessionMaker=SessionMaker
            )),

        (r'/view/([0-9]+)', ViewHandler, dict(
            SessionMaker=SessionMaker
            )),

        (r'/file/([0-9]+)/(.*)', DownloadHandler, dict(
            stored_docs_path=stored_docs_path
            )),

        (r'/orgs', OrgHandler, dict(
            SessionMaker=SessionMaker
            )),

        (r'/submitters', SubmitterHandler, dict(
            SessionMaker=SessionMaker
            ))

        ],

        template_path=template_path,
        debug=True
        )

    app.listen(8000)

    IOLoop.current().start()

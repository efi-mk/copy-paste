import json
import os
import server
import unittest
import tempfile

class CopyPasteTestCase(unittest.TestCase):
    def create_empty_user(self, name, text):
        """
        Add a new user to the db
        :param name: Name of the user to add
        :param text: Text that the user pasted
        """
        clip_element = server.Clipboard(username=name, text=text)
        self.db.session.add(clip_element)
        self.db.session.commit()

    def setUp(self):
        self.db_fd, self.name = tempfile.mkstemp()
        server.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % self.name
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        self.db = server.db
        self.db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.name)

    def test_user_not_found_when_trying_to_get(self):
        rv = self.app.get('/clipboard/efi')
        assert rv.status_code == 404

    def test_user_not_found_when_trying_to_post(self):
        rv = self.app.post('/clipboard/efi')
        assert rv.status_code == 404

    def test_user_pasted_text(self):
        self.create_empty_user('efi')
        rv = self.app.post('/clipboard/efi', data=json.dumps(dict(
            text="Hello World !")))
        assert rv.status_code == 200
        clip_element = server.Clipboard.query.filter_by(username='efi').first()
        assert clip_element.text == "Hello World !"

    def test_user_copying_text(self):
        self.create_empty_user('efi', "Hello 2")
        rv = self.app.get('/clipboard/efi')
        assert rv.status_code == 200
        result = json.loads(rv.data)
        assert result['text'] == "Hello 2"


if __name__ == '__main__':
    unittest.main()


#!/bin/bash
pyinstaller -F -w \
--hidden-import='email.mime.multipart' \
--hidden-import='email.mime.message' \
--hidden-import='email.mime.text' \
--hidden-import='email.mime.image' \
--hidden-import='email.mime.audio' \
--hidden-import='sqlalchemy.sql.default_comparator' \
--hidden-import='jinja2' \
--icon='./icons/spy_128.ico' \
main.py
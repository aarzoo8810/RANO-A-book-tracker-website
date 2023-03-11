from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from forms import AddRecord, Register, Login, AddPerson, Comment
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import PrimaryKeyConstraint
from datetime import datetime
from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from flask_gravatar import Gravatar
"""name of the website would be  RANO(RAito NOberu) is a japanese world which means light novel"""


rel_cover_folder_path = "static/assets/images/covers"


def str_to_date(str_date):
    """This function takes str date in format of 'yyyy-mm-dd' and returns python date object"""
    date = datetime.strptime(str_date, "%Y-%m-%d")
    return date

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)
SECRET_KEY = "i6jj97487u9e9387df87t8u875dru838757hru"
app.config["SECRET_KEY"] = SECRET_KEY


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    use_ssl=False,
                    base_url=None)

# connect to db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "instance/library.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# configure table
class Book(db.Model):
    __tablename__ = "books"
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    series = db.Column(db.String(255), nullable=False)
    volume_number = db.Column(db.Integer, nullable=False)
    release_date = db.Column(db.Date)
    description = db.Column(db.String)
    cover_image_location = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    illustrator_id = db.Column(db.Integer, db.ForeignKey("illustrators.id"))


class Authors(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True,
                          autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    dob = db.Column(db.Date)
    description = db.Column(db.String)


class Illustrator(db.Model):
    __tablename__ = "illustrators"
    id = db.Column(db.Integer, primary_key=True,
                                autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    dob = db.Column(db.Date)
    description = db.Column(db.String)


class AuthorsBooks(db.Model):
    __tablename__ = "authors_books"
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"))

    __table_args__ = (db.PrimaryKeyConstraint("author_id", "book_id"), )


class IllustratorsBooks(db.Model):
    __tablename__ = "illustrators_books"
    illustrator_id = db.Column(db.Integer, db.ForeignKey("illustrators.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"))

    __table_args__ = (db.PrimaryKeyConstraint("illustrator_id", "book_id"), )



class User(UserMixin, db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.String, nullable=False)

    __table_args__ = (db.UniqueConstraint('user_email'), )

    def get_id(self):
        return (self.user_id)


class Shelf(db.Model):
    __tablename__ = "shelves"
    shelf_id = db.Column(db.Integer, primary_key=True)
    shelf_name = db.Column(db.String(30), nullable=False)


class BookUser(db.Model):
    __tablename__ = "book_user"
    book_id = db.Column(db.Integer,
                        db.ForeignKey("books.book_id"),
                        nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    shelf_id = db.Column(db.Integer,
                        db.ForeignKey("shelves.shelf_id"),
                        nullable=False)
    # book_user_id = db.Column(db.Integer, primary_key=True)

    __table_args__ = (db.PrimaryKeyConstraint("book_id", "user_id"), )


class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

class ReadCompleteDate(db.Model):
    __tablename__ = "read_complete_date"
    book_id = db.Column(db.Integer,
                        db.ForeignKey("books.book_id"),
                        nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    
    start_date = db.Column(db.Date)
    complete_date = db.Column(db.Date)

    __table_args__ = (db.PrimaryKeyConstraint("book_id", "user_id"), )



with app.app_context():
    db.create_all()

# with app.app_context():
#     read_shelf = Shelf(shelf_name="read")
#     reading_shelf = Shelf(shelf_name="reading")
#     plan_to_read_shelf = Shelf(shelf_name="plan to read")
#     db.session.add(read_shelf)
#     db.session.add(reading_shelf)
#     db.session.add(plan_to_read_shelf)
#     db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    books = Book.query.all()
    return render_template("index.html",
                           books=books,
                           cover_folder_path=rel_cover_folder_path,
                           logged_in=current_user.is_authenticated,
                           current_user=current_user)


@app.route("/book/<book_id>", methods=["GET", "POST"])
def page_info(book_id):
    comment_form = Comment()

    if request.method == "POST":
        if comment_form.validate_on_submit:
            comment = request.form.get("comment")
            book_id = book_id
            user_id = current_user.user_id

            new_comment = Comments(
                comment=comment,
                book_id=book_id,
                user_id=user_id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("page_info", book_id=book_id))

    book = db.get_or_404(Book, book_id)
    # TODO: Below line will give 404 error because there is no comment in comment table and book id
    comments = Comments.query.filter_by(book_id=book_id).all()
    commenttext_username_userid_list = []
    for comment in comments:
        comment_text = comment.comment
        user_id = comment.user_id
        user = db.get_or_404(User, user_id)
        commenttext_username_userid_list.append((comment_text, user))

    author = db.get_or_404(Authors, book.author_id)
    try:
        illustrator = db.get_or_404(Illustrator, book.illustrator_id)
    except:
        illustrator=None
    shelves = Shelf.query.all()
    if current_user.is_authenticated:
        user_id = current_user.user_id
        book_user = BookUser.query.filter_by(book_id=book_id,
                                             user_id=user_id).first()
        
        if book_user is not None:
            user_book_shelf_id = book_user.shelf_id
            user_book_shelf_name = db.get_or_404(Shelf, user_book_shelf_id).shelf_name.title()

            return render_template("book-info.html",
                                    book=book,
                                    shelves=shelves,
                                    author=author,
                                    illustrator=illustrator,
                                    user_shelf=user_book_shelf_name,
                                    logged_in=current_user.is_authenticated,
                                    current_user=current_user,
                                    form=comment_form,
                                    comments=commenttext_username_userid_list)
        
    return render_template("book-info.html",
                            book=book,
                            author=author,
                            illustrator=illustrator,
                            shelves=shelves,
                            logged_in=current_user.is_authenticated,
                            current_user=current_user,
                            form=comment_form,
                            comments=commenttext_username_userid_list)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = AddRecord()
    if form.validate_on_submit():
        title = request.form.get("title").strip()
        series = request.form.get("series").strip()
        volume_number = request.form.get("volume_number")
        author_id = int(request.form.get("author_id"))
        illustrator_id = request.form.get("illustrator_id")

        if len(illustrator_id) > 0:
            illustrator_id = int(illustrator_id)
        else:
            illustrator_id = None

        release_date = str_to_date(request.form.get("release_date"))
        print(f"{release_date = }")
        description = request.form.get("description").strip()
        cover = form.cover.data

        # cover file name convention
        # <title>_<author>_<volume_num_of_book>.<extension_of_file>
        cover_filename = f"{title}-{author_id}-{volume_number}\
        .{secure_filename(cover.filename).split('.')[-1].strip()}"

        # save file in assets/cover folder
        cwd = os.getcwd()
        cover_image_abs_path = os.path.join(BASE_DIR,
                                            rel_cover_folder_path,
                                            cover_filename)

        print(f"{secure_filename(cover.filename) = }")
        print(f"{title = }")
        print(f"{series = }")

        # add book information to the database
        new_book = Book(
            title=title,
            series=series,
            volume_number=volume_number,
            author_id=author_id,
            illustrator_id=illustrator_id,
            release_date=release_date,
            description=description,
            cover_image_location=cover_filename
        )

        db.session.add(new_book)
        cover.save(cover_image_abs_path)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add.html",
                            form=form,
                            logged_in=current_user.is_authenticated,
                            current_user=current_user)


@app.route("/book/<book_id>/update", methods=["GET", "POST"])
@login_required
def update_book(book_id):
    print(f"{book_id = }")
    book = db.get_or_404(Book, book_id)
    form = AddRecord()
    old_book_title = book.title
    old_author = db.get_or_404(Authors, book.author_id)
    old_volume_number = book.volume_number
    old_cover = book.cover_image_location

    if request.method == "POST" and form.validate_on_submit:
        book.title = form.title.data.strip()
        book.series = form.series.data.strip()
        book.volume_number = form.volume_number.data
        book.author_id = int(form.author_id.data)

        illustrator_id = form.illustrator_id.data
        if len(illustrator_id) > 0:
            illustrator_id = int(illustrator_id)
        else:
            illustrator_id = None
        
        book.illustrator_id = illustrator_id
        
        book.release_date = form.release_date.data
        book.description = form.description.data.strip()
        cover_data = form.cover.data
        
        # this condition is true when a user uploads a file, and
        # It updates image data in filesystem with file extension
        # for file name this only changes file extension and binary data, not the actual name
        if cover_data is not None:
            new_file_extension = secure_filename(cover_data.filename).split(".")[-1]
            new_cover_name = f"{old_cover[:-4]}.{new_file_extension}"
            cover_data.save(os.path.join(BASE_DIR, rel_cover_folder_path, old_cover))
            os.rename(f"{rel_cover_folder_path}/{old_cover}", f"{rel_cover_folder_path}/{new_cover_name}")

        # this condition is true when a user changes title or author or volume_number of the book and
        # changes the file name of the images based on those changes.
        if old_book_title != book.title or old_author != book.series or old_volume_number != book.volume_number:
            old_file_extension = old_cover.split(".")[-1]
            new_cover_name = f"{book.title}-{book.author_id}-{book.volume_number}.{old_file_extension}"
            book.cover_image_location = new_cover_name
            os.rename(f"{rel_cover_folder_path}/{old_cover}", f"{rel_cover_folder_path}/{new_cover_name}")

        db.session.commit()

        return redirect(url_for('home'))

    form.title.data = book.title
    form.series.data = book.series
    form.volume_number.data = book.volume_number
    form.author_id.data = book.author_id
    form.illustrator_id.data = book.illustrator_id
    form.release_date.data = book.release_date
    form.description.data = book.description
    
    img_bin_data = os.path.join(BASE_DIR,
                                   rel_cover_folder_path,
                                   book.cover_image_location)
    form.cover.data = img_bin_data

    return render_template("add.html",
                            update_form=form,
                            logged_in=current_user.is_authenticated,
                            current_user=current_user)


@app.route("/book-details/<book_id>_<book_title>_<shelf_id>_<user_list>", methods=["GET", "POST"])
def add_to_shelf(book_id, book_title, shelf_id, user_list):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        book_user = BookUser.query.filter_by(book_id=book_id, user_id=current_user.user_id).first()
        user_id = current_user.user_id

        if book_user is not None:
            book_user.book_id=book_id
            book_user.user_id=user_id
            book_user.shelf_id=shelf_id
        else:
            new_book_user = BookUser(book_id=book_id, user_id=user_id, shelf_id=shelf_id)
            db.session.add(new_book_user)

        db.session.commit()
        print(f"{type(user_list)}")
        if user_list == "True":
            return redirect(url_for("user_book_list", user_name=current_user.user_name))
        else:
            return redirect(url_for("page_info", book_id=book_id, book_title=book_title))

@app.route("/book-details/<book_id>_<book_title>/remove")
def delete_from_user_list(book_id, book_title):
    user_id = current_user.user_id
    
    book_user_shelf = BookUser.query.filter_by(book_id=book_id,
                                               user_id=user_id).first()
    if book_user_shelf is not None:
        db.session.delete(book_user_shelf)
        db.session.commit()
        flash("Deleted Successfully")
    else:
        flash("Could not delete, maybe Try again")

    return(redirect(url_for("user_book_list", user_name=current_user.user_name)))

@app.route("/register", methods=["GET", "POST"])
def register():
    error=None
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        register_form = Register()
        if register_form.validate_on_submit():
            user_name =  register_form.user_name.data.strip()
            user_email = register_form.email.data.strip()
            raw_password = register_form.password.data.strip()
            
            user = User.query.filter_by(user_email=user_email).first()
            if user is not None:
                error = "Email already exist."
                # return redirect(url_for('register', error=error))
            
            else:
                hash_password = generate_password_hash(raw_password,
                                                       method="pbkdf2:sha256",
                                                       salt_length=8)

                new_user = User(
                    user_name=user_name,
                    user_email=user_email,
                    user_password=hash_password
                )
                db.session.add(new_user)
                db.session.commit()
                
                user = User.query.filter_by(user_email=user_email).first()
                login_user(user)

                flash("Account created, and successfully logged in.")
                return redirect(url_for('home'))
        return render_template("register-user.html", register_form=register_form, error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        login_form = Login()

        if request.method == "POST":
            if login_form.validate_on_submit:
                email = login_form.email.data
                password = login_form.password.data

                user = User.query.filter_by(user_email=email).first()
                if user is not None:
                    if check_password_hash(user.user_password, password):
                        login_user(user)
                        # flash("Successfully logged in.")
                        return redirect(url_for('home'))
                    else:
                        error = "Wrong Password"
                else:
                    error = "Wrong Email"

        return render_template("login.html",
                                login_form=login_form, 
                                error=error)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/user/<user_name>/list")
def user_book_list(user_name):
    if user_name != current_user.user_name:
        return abort(404, "404, user not found")
    else:
        user_books = BookUser.query.filter_by(user_id=current_user.user_id)
        shelves = Shelf.query.all()
        book_shelf_list = []
        for user_book in user_books:
            book_id = user_book.book_id
            shelf_id = user_book.shelf_id
            book = Book.query.filter_by(book_id=book_id).first()
            shelf = Shelf.query.filter_by(shelf_id=shelf_id).first()
            author = Authors.query.filter_by(id=book.author_id).first()
            illustrator = Illustrator.query.filter_by(id=book.illustrator_id).first()
            book_shelf = (book, shelf, author, illustrator)
            book_shelf_list.append(book_shelf)

        return render_template("user-book-list.html", 
                                user_books=book_shelf_list,
                                shelves=shelves,
                                current_user=current_user,
                                logged_in=current_user.is_authenticated)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        key_word = request.form.get("search")
        
        if key_word.startswith(">>"):
            key_word = key_word.replace(">>", "").strip()
            authors = Authors.query.filter(Authors.name.like('%' + key_word + '%')).all()
            illustrators = Illustrator.query.filter(Illustrator.name.like('%' + key_word + '%')).all()

            return render_template("person-search-result.html",
                                    logged_in=current_user.is_authenticated, 
                                    authors=authors,
                                    illustrators=illustrators,
                                    searched_word=key_word,)
        else:
            result_books = Book.query.filter(Book.title.like('%'+ key_word + '%')).all()
            return render_template("search-result.html",
                                    searched_books=result_books,
                                    searched_word=key_word,
                                    logged_in=current_user.is_authenticated)
    
    return abort(404)


@app.route("/add-person", methods=["GET", "POST"])
def add_person():
    form = AddPerson()
    if request.method == "POST":
        if form.validate_on_submit:
            name = request.form.get("name")
            dob = str_to_date(request.form.get("dob"))
            job = request.form.get("job")
            description = request.form.get("description").strip()

            if job == "Author":
                new_author = Authors(
                    name=name,
                    dob=dob,
                    description=description
                )
                print(f"{db.session.add(new_author)}")
                print(f"{db.session.commit()}")
                print(f"{new_author.id = }")
            else:
                new_illustrator = Illustrator(
                    name=name,
                    dob=dob,
                    description=description
                )
                print(f"{db.session.add(new_illustrator)}")
                db.session.commit()



            return f"{name = }\n{dob = }\n{job = }\n{description = }"
    return render_template("add-person.html", 
                            form=form, 
                            logged_in=current_user.is_authenticated)


@app.route("/person/<profession>/<id>")
def person_book_list(profession, id):
    person = None
    if profession == "author":
        person = Authors.query.filter_by(id=id).first()
    else:
        person = Illustrator.query.filter_by(id=id).first()
    
    person_books = None
    if person:
        person_books = Book.query.filter_by(author_id=person.id)
    
    return render_template("search-result.html", person=person, person_books=person_books,
                            logged_in=current_user.is_authenticated)


@app.route("/post-comment/<book_id>", methods=["GET", "POST"])
def add_comment(book_id):
    
    
    return redirect(url_for("page_info", book_id=book_id))


@app.route("/check")
@login_required
def check():
    return "Hello"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

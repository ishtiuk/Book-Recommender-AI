from flask import Flask, render_template, request, redirect, url_for
from pickle import load
import numpy as np


app = Flask(__name__)

similarity_scores = load(open("model/similarity_scores.bin", "rb"))
## database/ dataframe loading...
popular_df = load(open("model/popular_df.bin", "rb"))
final_filtered = load(open("model/final_filtered.bin", "rb"))
train_pivot_table = load(open("model/train_pivot_table.bin", "rb"))

## engines loading...
# cosine_similarity = load(open("model/cosine_similarity.bin", "rb"))


## search suggestions...randomly choosen..
books = final_filtered["Book-Title"].unique()
search_suggestions_idx = list(books[np.random.randint(0, len(books), 15)])
search_suggestions = list(map(lambda x : x.title(), search_suggestions_idx))



@app.route("/")
def index():
    top_30 = popular_df.iloc[:30, ].copy()
    top_30["Book-Title"] = top_30["Book-Title"].apply(lambda x : x.title())
    img_links = top_30["Image-URL-L"].values.tolist()
    book_names = top_30["Book-Title"].values.tolist()
    author_names = top_30["Book-Author"].values.tolist()
    total_votes = top_30["num_rating"].values.tolist()
    avg_rating = top_30["avg_rating"].values.tolist()


    return render_template("index.html", img_links=img_links, book_names=book_names, author_names=author_names, total_votes=total_votes, avg_rating=avg_rating)



@app.route("/recommend")
def recommend_load_ui():
    
    return render_template("recommendation.html", search_suggestions=search_suggestions)


@app.route("/recommend_books", methods=["POST"])
def recommend():
    usr_input = str(request.form.get("usr_input")).lower().split()
    book_name = " ".join(usr_input)
    output = "Recommended Books"
    datas = []

    try:
        idx = np.where(train_pivot_table.index == book_name)[0][0]
        most_similar_idx = np.argsort(similarity_scores[idx])[::-1][1:7]
            
        
        for book in np.array(train_pivot_table.index)[most_similar_idx]:
            desc_book = final_filtered.loc[(final_filtered["Book-Title"] == book)].iloc[0, ]
            book_datas = [desc_book["Image-URL-L"], desc_book["Book-Title"].title(), desc_book["Book-Author"], desc_book["Year-Of-Publication"], desc_book["Publisher"]]
            datas.append(book_datas)
    except:
        output = False
        datas = "Sorry, Book Not Found!"

    return render_template("recommendation.html", datas=datas, output=output, search_suggestions=search_suggestions)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


## Feedback transmission system via mail.. ;)
def feedback_mail(message):
    import smtplib
    from datetime import datetime

    message = message + "\nUTC time: " + datetime.isoformat(datetime.utcnow())
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("feedbackbookrecommenderr@gmail.com", "kfetbwajqhdytdck")
    s.sendmail("feedbackbookrecommenderr@gmail.com", "deltagon@protonmail.com", message)
    s.quit()


@app.route('/6810c3c04069ca9707728937d8', methods=['POST'])
def fetch_feedback():
    name = str(request.form.get('name'))
    email = str(request.form.get('email'))
    message = str(request.form.get('message'))

    if len(name) > 0 or len(email) > 0 or len(message) > 0:
        feedback_mail(f"[Book Recommender Feedback Bot]\nName- {name}\nMail- {email}\nFeedback- {message}")

        return render_template('contact.html', tnx_feedback="Thank you for feedback!")
    return redirect(url_for('contact'))


if __name__ == "__main__":
    app.run()

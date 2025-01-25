# Quickwrite: A blog based on gists
Quickwrite is a pretty blog system that uses github gists as the backend!

# How it works
1. You create a markdown gist on github or use quickwrite's built in editor
    a. If you're making a gist, the file format is `quickwrite--<title>.md`
2. You sign in to Quickwrite with your github account
3. Quickwrite fetches all your gists and displays them as blog posts!

# Features
- [x] Sign in with github
- [x] Fetch gists
- [x] Display gists as blog posts
- [x] Create notes with a built-in editor
- [x] Profile pages
- [ ] Edit/delete notes
- [ ] Comments

# Self hosting
1. Clone the repo
2. Run `pip install -r requirements.txt`
3. Create an oauth app on github
4. Copy `.env.example` to `.env` and fill in the required fields
5. Run `python main.py`
# simple_text_classifier

Tools for classifying text files using models built with training examples

* Performs well on the 20 Newsgroups Dataset (http://qwone.com/~jason/20Newsgroups/)
* Supports basic removal of stop words and stop characters
* Supports use of n-grams in the model - default is 2
 
The training and classification logic are all in the utils/models.py package, so you can incorporate them into any implementation. The included train.py and classify.py import defs from these packages and can be used as a reference.

This project is intended as a teaching example for text processing with python - not a production text classifier. Try scikit-learn (http://scikit-learn.org/stable/) for that.

---

# Example using 20 Newsgroups Dataset:

1. Download the simple_text_classifier distribution, and install it:

```
spair13:simple_text_classifier sid$ pwd
/Users/sid/code/simple_text_classifier

spair13:simple_text_classifier sid$ ls -l
total 24
-rw-r--r--  1 sid  staff  1083 May  4  2016 LICENSE.txt
-rw-r--r--  1 sid  staff   780 Apr  6 12:46 README.md
-rw-r--r--  1 sid  staff   780 Apr  6 12:45 README.txt
drwxr-xr-x  8 sid  staff   256 Apr  4 13:45 simple_text_classifier/

spair13:simple_text_classifier sid$ 
```

2. Download the 20 Newsgroups Data Set using the URL above...

3. The corpus consists of email messages in labeled folders

For each group you want to train models and classify against, first move ~20% of the documents into a separate directory with the name "test" added. Leave the remaining 80% for training. The ones removed will be used to test the classifier (and models) and verify that they are working.

```
spair13:20news-train sid$ pwd
/Users/sid/data/20news-train
spair13:20news-train sid$ ls -l
total 0
drwxr-xr-x@  784 sid  staff  25088 May  2  2017 alt.atheism/
drwxr-xr-x@  968 sid  staff  30976 May  2  2017 comp.graphics/
drwxr-xr-x@  987 sid  staff  31584 Sep 26  2001 comp.os.ms-windows.misc/
drwxr-xr-x@  984 sid  staff  31488 Sep 26  2001 comp.sys.ibm.pc.hardware/
drwxr-xr-x@  963 sid  staff  30816 Sep 26  2001 comp.sys.mac.hardware/
drwxr-xr-x@  982 sid  staff  31424 Sep 26  2001 comp.windows.x/
drwxr-xr-x@  974 sid  staff  31168 Sep 26  2001 misc.forsale/
drwxr-xr-x@  985 sid  staff  31520 May  2  2017 rec.autos/
drwxr-xr-x@  996 sid  staff  31872 Sep 26  2001 rec.motorcycles/
drwxr-xr-x@  996 sid  staff  31872 Sep 26  2001 rec.sport.baseball/
drwxr-xr-x@ 1001 sid  staff  32032 Sep 26  2001 rec.sport.hockey/
drwxr-xr-x@  987 sid  staff  31584 May  2  2017 sci.crypt/
drwxr-xr-x@  983 sid  staff  31456 Sep 26  2001 sci.electronics/
drwxr-xr-x@  992 sid  staff  31744 Apr  4 21:36 sci.med/
drwxr-xr-x@  989 sid  staff  31648 Sep 26  2001 sci.space/
drwxr-xr-x@  993 sid  staff  31776 May  7  2017 soc.religion.christian/
drwxr-xr-x@  907 sid  staff  29024 May  7  2017 talk.politics.guns/
drwxr-xr-x@  936 sid  staff  29952 Apr  4 21:35 talk.politics.mideast/
drwxr-xr-x@  777 sid  staff  24864 Sep 26  2001 talk.politics.misc/
drwxr-xr-x@  630 sid  staff  20160 Sep 26  2001 talk.religion.misc/
```
4. Build a reference classification model known as the "IDF" (Inverse Document or Database Frequency) from all the files. This data is essential to classification as it provides term frequency information from as much text as possible. 

The -r switch tells train.py to recurse through all subdirectories and put it all into one model.

```
spair13:20news-train sid$ python ~/code/simple_text_classifier/simple_text_classifier/train.py -o ~/data/idf.g3.model -c -s -r -g 3 "./*"
train.py: reading: ./talk.politics.mideast/75895 ok, training... ok
  ...etc...
train.py: reading: ./talk.religion.misc/82815 ok, training... ok
train.py: finalizing model... ok
train.py: saving model... ok
spair13:20news-train sid$ ls -l ~/data/idf.g3.model 
-rw-r--r--  1 sid  staff  158099358 Apr  6 19:04 /Users/sid/data/idf.g3.model
```

5. Build a model for one of the groups, using the training set. We do not use the -r switch in this case, since the model should be trained using only the documents in the labeled directory.

```
spair13:talk.politics.mideast sid$ python ~/code/simple_text_classifier/simple_text_classifier/train.py -o ~/data/talk.politics.mideast.g3.model -c -s -g 3 "./*"
train.py: reading: ./75895 ok, training... ok
  ...etc...
train.py: reading: ./76001 ok, training... ok
train.py: finalizing model... ok
train.py: saving model... ok
spair13:talk.politics.mideast sid$ ls -l ~/data/talk.politics.mideast.g3.model 
-rw-r--r--  1 sid  staff  15313789 Apr  6 19:05 /Users/sid/data/talk.politics.mideast.g3.model
```

6. Verify that the model works using the test set from the same group. Most if not all documents should match, with high scores.

```
spair13:talk.politics.mideast sid$ python ~/code/simple_text_classifier/simple_text_classifier/classify.py -m ~/data/talk.politics.mideast.g3.model -i ~/data/idf.g3.model -c -s -g 3 "./*"
classify.py: reading input model: /Users/sid/data/talk.politics.mideast.g3.model ok
classify.py: reading idf model: /Users/sid/data/talk.politics.mideast.g3.model ok
classify.py: reading: ./75408 matches model: 1.00 *
classify.py: reading: ./75913 matches model: 1.00 *
classify.py: reading: ./75909 matches model: 1.00 *
classify.py: reading: ./75930 matches model: 1.00 *
classify.py: reading: ./75873 matches model: 1.00 *
classify.py: reading: ./75369 matches model: 1.00 *
classify.py: reading: ./75394 matches model: 1.00 *
```
 
7. Verify that the model works by classifying the test set from a different group. Few if any documents should match, with low scores.

```
spair13:rec.autos sid$ python ~/code/simple_text_classifier/simple_text_classifier/classify.py -m ~/data/talk.politics.mideast.g3.model -i ~/data/idf.g3.model -c -s -g 3 "./*"
classify.py: reading input model: /Users/sid/data/talk.politics.mideast.g3.model ok
classify.py: reading idf model: /Users/sid/data/talk.politics.mideast.g3.model ok
classify.py: reading: ./101609 matches model: 0.20
classify.py: reading: ./101601 matches model: 0.20
classify.py: reading: ./101591 matches model: 0.15
classify.py: reading: ./101597 matches model: 0.25
classify.py: reading: ./101555 matches model: 0.10
classify.py: reading: ./101573 matches model: 0.15
classify.py: reading: ./101581 matches model: 0.20
classify.py: reading: ./101592 matches model: 0.20
```

Note that the classifier may have trouble distinguishing messages from groups with similar subjects like soc.religion.christian and alt.atheism. Adding more training data could help...  

8. Report any issues to the author..!

---

# train.py
Creates (trains) a classification model using one or text files 

## Usage
```
python train.py [-h] [-o OUTPUTFILE] [-c] [-s] [-r] [-t] [-g GRAMS] filespec
```

## Arguments
```
-h requests help
-o OUTPUTFILE specifies the path to save the model file
-c removes stop characters
-s removes stop words
-r recurses through subdirectories; unless specified, train.py operates only on the current directory
-t specifies that the top 20 entries in the model should be displayed
-g GRAMS specifies the number of grams (word combinations) to use in modelling filespec must be the path to one or more text files
```

## Notes
* Models are stored as text, and currently all words and optionally n-grams are stored, even if they never contribute; this will be fixed in a future release
* Use the -r switch with all available training content to create an IDF model as shown in the example (above)
* Using -g 3 seems to produce optimal results on the 20 Groups set. Higher values are unlikely to produce recall on such a small amount of data.

---

# classify.py
Determines the similarity between a classification model, and one or text files, using a reference IDF file 

## Usage
```
python classify.py [-h] [-c] [-s] [-g GRAMS] filespec
```

## Arguments
```
-h requests help
-c removes stop characters
-s removes stop words
-g GRAMS specifies the number of grams (word combinations) to use in modelling filespec must be the path to one or more text files
```

## Notes
* The score produced for each file ranges from 0 to 1.0
* Scores over .667 are considered a match
* Using -g 3 seems to produce optimal results on the 20 Groups set. Higher values are unlikely to produce recall on such a small amount of data.

---

# To Do

* Use numbers instead of strings
* Remove irrelevant words & grams
* Faster scoring/sorting
* Real confidence score
* Support other input formats
* Handle email format - currently the trainer learns email addresses, etc which is not ideal

---

# Reference

* https://en.wikipedia.org/wiki/Document_classification
* https://en.wikipedia.org/wiki/Precision_and_recall

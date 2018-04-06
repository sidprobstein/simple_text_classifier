# simple_text_classifier

Tools for classifying text files using models built with training examples

* Performs well on the "20 Groups" test corpus (http://qwone.com/~jason/20Newsgroups/)
* Supports basic removal of stop words and stop characters
* Supports use of n-grams in the model - default is 2
 
The training and classification logic are all in the utils/models.py package, 
so you can incorporate them into your own implementations as needed. The included train.py
and classify.py import these packages and can be used as a reference implementation.


---

# Example using 20 Groups:

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
drwxr-xr-x  3 sid  staff    96 Apr  4 21:38 tests/

spair13:simple_text_classifier sid$ 
```

2. Download the 20 Groups test using the URL above...

3. The corpus consists of messages from 20 news groups, in email format, each in 
a labelled folder. 

For each group you want to train models and classify against, 
move ~20% of the documents into a separate directory with the name "test" added. 
The remaining 80% of the documents will be used to train the classifier. The ones
removed will be used to test the classifier and verify that it is working.

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
4. Build a reference model known as the "IDF" (Inverse Document or Database Frequency) 
from all the files. This data is essential to classification as it provides term
frequency information across the language in question. 

Note the use of the -r switch to recurse through all subdirectories.

```
spair13:20news-train sid$ python ~/code/simple_text_classifier/simple_text_classifier/train.py -o ~/data/idf.g3.model -c -s -g 3 -r  "./*"
train.py: reading: ./talk.politics.mideast/75895
...etc...
train.py: reading: ./talk.religion.misc/82815
simple_text_classifier.common.models.py: save_classification_model: writing: /Users/sid/data/idf.g3.model ok
spair13:20news-train sid$ ls -l ~/data/idf.g3.model
-rw-r--r--  1 sid  staff  158099358 Apr  6 15:37 /Users/sid/data/idf.g3.model
```

5. Build a model for one of the groups, using the training set. Here we do not use
the -r switch, we are building a model just from the files inside one of the training 
directories.

```
spair13:talk.politics.mideast sid$ python ~/code/simple_text_classifier/simple_text_classifier/train.py -o ~/data/talk.politics.mideast.g3.model -c -s -g 3  "./*"
train.py: reading: ./75895
...etc...
train.py: reading: ./76001
simple_text_classifier.common.models.py: save_classification_model: writing: /Users/sid/data/talk.politics.mideast.g3.model ok
spair13:talk.politics.mideast sid$ ls -l ~/data/talk.politics.mideast.g3.model 
-rw-r--r--  1 sid  staff  15313789 Apr  6 15:39 /Users/sid/data/talk.politics.mideast.g3.model
```

6. Verify that the model works using the test set from the same group. Most if not
all documents should match with 90%+ confidence.

```
spair13:talk.politics.mideast sid$ pwd
/Users/sid/data/20news-test/talk.politics.mideast
spair13:talk.politics.mideast sid$ python ~/code/simple_text_classifier/simple_text_classifier/classify.py -m ~/data/talk.politics.mideast.g3.model -i ~/data/idf.g3.model -c -s -g 3 "./*"
simple_text_classifier.common.models.py: load_classification_model: reading: /Users/sid/data/talk.politics.mideast.g3.model ok
simple_text_classifier.common.models.py: load_classification_model: reading: /Users/sid/data/idf.g3.model ok
classify.py: reading: ./75408 matches model: 1.00 *
classify.py: reading: ./75913 matches model: 1.00 *
classify.py: reading: ./75909 matches model: 1.00 *
classify.py: reading: ./75930 matches model: 1.00 *
classify.py: reading: ./75873 matches model: 1.00 *
classify.py: reading: ./75369 matches model: 1.00 *
classify.py: reading: ./75394 matches model: 1.00 *
```
 
7. Verify that the model works by classifying the test set from a different group.
Most if not all documents should NOT match, with low confidence (below 50%).

```
spair13:rec.autos sid$ pwd
/Users/sid/data/20news-test/rec.autos
spair13:rec.autos sid$ python ~/code/simple_text_classifier/simple_text_classifier/classify.py -m ~/data/talk.politics.mideast.g3.model -i ~/data/idf.g3.model -c -s -g 3 "./*"
simple_text_classifier.common.models.py: load_classification_model: reading: /Users/sid/data/talk.politics.mideast.g3.model ok
simple_text_classifier.common.models.py: load_classification_model: reading: /Users/sid/data/idf.g3.model ok
classify.py: reading: ./101609 matches model: 0.20
classify.py: reading: ./101601 matches model: 0.20
classify.py: reading: ./101591 matches model: 0.15
classify.py: reading: ./101597 matches model: 0.25
classify.py: reading: ./101555 matches model: 0.10
classify.py: reading: ./101573 matches model: 0.15
classify.py: reading: ./101581 matches model: 0.20
classify.py: reading: ./101592 matches model: 0.20
```

Note that the classifier may have trouble distinguishing messages from groups with
overlapping subjects like soc.religion.christian and alt.atheism. Adding more training
data could help this situation. 

8. Report any issues to the author! Many thanks!

---

# train.py
Creates (trains) a classification model using one or text files 

## Usage
```
python train.py [-h] [-o OUTPUTFILE] [-c] [-s] [-r] [-t] [-g GRAMS] filespec
```

## Arguments
-h requests help
-o OUTPUTFILE specifies the path to save the model file
-c removes stop characters
-s removes stop words
-r recurses through subdirectories; unless specified, train.py operates only on 
the current directory
-t specifies that the top 20 entries in the model should be displayed
-g GRAMS specifies the number of grams (word combinations) to use in modelling
filespec must be the path to one or more text files

## Notes
* Models are stored as text, and currently all words and optionally n-grams are
stored, even if they never contribute; this will be fixed in a future release
* Use the -r switch with all available training content to create an IDF model as 
shown in the example (above)
* Using -g 3 seems to produce optimal results on the 20 Groups set. Higher values
are unlikely to produce recall on such a small amount of data.

---

# classify.py
Determines the similarity between a classification model, and one or text files,
using a reference IDF file 

## Usage
```
python classify.py [-h] [-c] [-s] [-g GRAMS] filespec
```

## Arguments
-h requests help
-c removes stop characters
-s removes stop words
-g GRAMS specifies the number of grams (word combinations) to use in modelling
filespec must be the path to one or more text files

## Notes
* The score produced for each file ranges from 0 to 1.0
* Scores over .667 are considered a match
* Using -g 3 seems to produce optimal results on the 20 Groups set. Higher values
are unlikely to produce recall on such a small amount of data.

---

# Further Reading

* https://en.wikipedia.org/wiki/Document_classification
* https://en.wikipedia.org/wiki/Precision_and_recall

# Internet of Kilos
www.iokilos.herokuapp.com
This is a website for Olympic Weightlifting Analysis. We are currently on the 1.0 version.

This is the first version of the website. In it you'll find:
1) A new approach to the SinClair Coefficient
2) Visual plots of world records in the different events and weight classes througout time, and also some facts about a few woeld records.
3) A Machine learning app that given your information, predicts what should be your goal for the next year.
4) A color coded map with containing information about the amount of world records broken by each country.

More Info:
This is work in progress. I'll eventually improve the Machine learning part, the difficulty is that it predicts well for lifters for which there is at least some previous data but it's hard to ask a web user to enter their competition history. I will also work some more on implementing a better statistical analysis for the world record's pattern.

__________________
This Heroku website is written in Python and uses, SKLearn/Machine-Learning (Naive Bayes and KNearestNeighbors), BeautifulSoup (for live webscraping), Bokeh, Cartodb, HTML/CSS and JavaScript.

Some data has been scraped and pickled as well as some Machine Learning models to decrease loading time.
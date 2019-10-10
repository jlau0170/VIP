from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.datasets import fetch_20newsgroups

documents = []
with open('results.txt') as inp:
    for line in inp:
        documents.append(line)



vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(documents)


true_k = 2
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
model.fit(X)

print("Top terms per cluster:")
order_centroids = model.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()
for i in range(true_k):
    print("Cluster %d:" % i),
    for ind in order_centroids[i, :5]:
        print(' %s' % terms[ind]),
    print


# Predicitng which clusters the phrases belong to -------------
# print("\n")
# print("Predictions")

# while True:
# 	s = input("Enter a phrase: ")
# 	Y = vectorizer.transform([s])
# 	prediction = model.predict(Y)
# 	print("The phrase", s, "is most likely in cluster", prediction[0])

# Y = vectorizer.transform(["there are many religions"])
# prediction = model.predict(Y)
# print(prediction)


"""
K-Means Clustering Algorithm:
2 Steps:
1) Cluster Assignment - Algorithm goes through each data point and assigns
the data point to one of the 3 (any #) of cluster centroid based on the Euclidean distance 
between each data instance and centroids of all the clusters
2) Centroid Movement - Moves the centroids to the average of the points around the cluster to centralize
the centroid location
The process is repeated until there is no change in the clusters 
"""
import glob
from collections import defaultdict, Counter
from pprint import pprint

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

TXTS_PATH = "/data/datagouv/data_gouv_txt"
txt_files = glob.glob(f"{TXTS_PATH}/**/*.txt", recursive=True)[:]
organisations = [o.split("/")[4] for o in txt_files]
y = organisations
vectorizer = HashingVectorizer(n_features=2 ** 10)
X = vectorizer.fit_transform(txt_files)
print(X.shape)
pca = TruncatedSVD(n_components=3, random_state=42).fit_transform(X)
tsne = TSNE(n_components=2, random_state=42).fit_transform(pca)

df = pd.DataFrame(tsne, columns=["x", "y"])
dict_label_index = defaultdict(list)
df["labels"] = y
for idx, label in enumerate(y):
    dict_label_index[label].append(idx)
freq_orgs = Counter(y)
top_10_labels = [t[0] for t in freq_orgs.most_common(10)]
pprint(sorted(freq_orgs.most_common(10), key=lambda x: x[1], reverse=True))
sampled_y = []
sampled_values = []
for val in top_10_labels:
    sampled_values.extend(dict_label_index[val])
    sampled_y.extend([val] * len(dict_label_index[val]))
sampled_df = df.iloc[sampled_values]
sampled_df.loc[:, "labels"] = sampled_y

fig = plt.figure(figsize=(16, 10))
g = sns.scatterplot(
    x="x", y="y",
    hue="labels",
    palette=sns.color_palette("hls", 10),
    data=sampled_df,
    legend="brief",
    alpha=0.3
)

plt.legend(bbox_to_anchor=(0.65, -0.1), loc=1, borderaxespad=0.)
fig.savefig('t-sne.png', bbox_inches='tight')

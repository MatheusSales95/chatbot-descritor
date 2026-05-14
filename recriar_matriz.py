import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

labels = ['calculate_area', 'count_events', 'ranking_eventos']

cm = np.array([
    [11, 2,  4],
    [ 3, 8,  1],
    [ 2, 0, 10],
])

fig, ax = plt.subplots(figsize=(12, 10))

sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    xticklabels=labels,
    yticklabels=labels,
    cmap='Blues',
    annot_kws={"size": 24},
    ax=ax,
)

ax.set_title('Matriz de Confusão: Intenções Reais vs Preditas', fontsize=24, pad=20)
ax.set_ylabel('Verdadeiro', fontsize=24, labelpad=12)
ax.set_xlabel('Predito', fontsize=24, labelpad=12)
ax.tick_params(axis='x', labelsize=24)
ax.tick_params(axis='y', labelsize=24)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=24)

plt.tight_layout()
plt.savefig("matriz_confusao.png", dpi=300)
print("matriz_confusao.png salva com sucesso.")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")

def box(x, y, w, h, txt, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4", fc=color, ec="#333", lw=1.2))
    ax.text(x + w/2, y + h/2, txt, ha="center", va="center", fontsize=9, family="Arial")

def arrow(x1, y1, x2, y2, txt, dy=2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="<->", lw=1.4, color="#222"))
    ax.text((x1+x2)/2, (y1+y2)/2 + dy, txt, ha="center", fontsize=8, family="Arial")

box(2, 18, 20, 16, "PC del operador\nPostman\nScripts Python\n(requests, ncclient)", "#dbeafe")
box(33, 36, 22, 10, "Túnel VPN\n(OpenConnect/AnyConnect)\nred 10.10.20.0/24", "#fef3c7")
box(66, 18, 30, 16, "Router Cisco Catalyst 8000v\nIOS XE 17.12 (10.10.20.48)\nModelos YANG ietf-interfaces\ny ietf-ip", "#dcfce7")
box(33, 3, 22, 10, "API REST de Webex\nwebexapis.com/v1/messages", "#fce7f3")
box(70, 3, 26, 10, "Sala de Webex\n\"CE5301 - Alertas de red\"", "#fce7f3")

arrow(22, 28, 33, 40, "", 0)
arrow(55, 40, 66, 30, "", 0)
ax.text(44, 31, "RESTCONF: HTTPS 443 (JSON)\nNETCONF: SSH 830 (XML)", ha="center", fontsize=8, family="Arial")
arrow(22, 22, 33, 9, "HTTPS 443\n(Bearer token)", 2)
arrow(55, 8, 70, 8, "mensaje", 1.5)
plt.tight_layout()
plt.savefig("figuras/arquitectura.png", dpi=200)

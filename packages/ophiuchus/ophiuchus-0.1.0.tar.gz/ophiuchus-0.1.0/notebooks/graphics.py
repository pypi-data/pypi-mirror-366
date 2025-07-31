from model.base.utils import InternalState
import numpy as np
from einops import rearrange
from moleculib.protein.alphabet import all_residues
from moleculib.protein.datum import ProteinDatum
from moleculib.protein.transform import DescribeChemistry
import plotly.graph_objects as go

import jax
import jax.numpy as jnp 

import py3Dmol
import numpy as np
import jaxlib
import plotly as plt 

def _maybe_cast_to_float32(x):
    if type(x) == jnp.ndarray or type(x) == np.ndarray or type(x) == jaxlib.xla_extension.ArrayImpl:
        if x.dtype == jnp.bfloat16:
            return x.astype(jnp.float32)
    return x

prepare_pdb = lambda datum: jax.tree_util.tree_map(_maybe_cast_to_float32, datum).to_pdb_str()

def viz_datum_grid(data, window_size=(600, 600), linked=True):
    v = py3Dmol.view(viewergrid=(1, len(data)), linked=linked, width=len(data) * window_size[0], height=window_size[1])

    for idx, datum in enumerate(data):
        if type(datum) == ProteinDatum:
            v.addModel(prepare_pdb(datum), 'pdb',  viewer=(0,idx))
            v.setStyle({'cartoon': {'color': 'spectrum'}, 'stick': {'radius': 0.2}}, viewer=(0,idx))
        elif type(datum) == InternalState:
            vectors = rearrange(datum.irreps_array.filter('1e').array, '... (d c) -> ... d c', c=3)
            for coord, vecs, mask in zip(datum.coord, vectors, datum.mask):
                if mask is False:
                    continue
                x, y, z = coord
                x, y, z = float(x), float(y), float(z)
                for (dx, dy, dz) in vecs:
                    v.addArrow({"start": {"x":x, "y":y, "z":z}, "end": {"x": x + float(dx), "y": y +float(dy), "z": z +float(dz)}, 'radius': 0.04, 'mid':0.95, 'color': color})    
    v.setBackgroundColor('rgb(0,0,0)', 0)
    v.zoomTo()
    
    return v

def viz_datum(data, window_size=(600, 600)):
    v = py3Dmol.view(width=window_size[0], height=window_size[1])

    for idx, (datum, color) in enumerate(zip(data, plt.colors.DEFAULT_PLOTLY_COLORS)):
        v.addModel(prepare_pdb(datum), 'pdb')
        v.setStyle({'model':idx}, {'cartoon': {'color': color}, 'stick': {'radius': 0.2, 'color': color} })
    
    v.setBackgroundColor('rgb(0,0,0)', 0)
    v.zoomTo()
    
    return v

def viz_spheres(vecs, radius=0.1, window_size=(300, 300), color='gray'):
    v = py3Dmol.view(width=window_size[0], height=window_size[1])
    for (x, y, z) in vecs:
        x, y, z = float(x), float(y), float(z)
        if x == 0.0 and y == 0.0 and z == 0.0:
            continue
        v.addSphere({"center": {"x": x, "y": y, "z": z}, 'radius': radius, 'color': color})
        v.zoomTo()
    # v.addSphere({"center": {"x": 0.0, "y": 0.0, "z": 0.0}, 'radius': 1.0, 'color': 'rgba(10, 10, 10, 0.5)'})
    v.setBackgroundColor('rgb(0,0,0)', 0)
    return v

def viz_internals(state, window_size, color='gray'):
    v = py3Dmol.view(width=window_size[0], height=window_size[1])
    vectors = rearrange(state.irreps_array.filter('1e').array, '... (d c) -> ... d c', c=3)
    for coord, vecs, mask in zip(state.coord, vectors, state.mask):
        if mask is False:
            continue
        x, y, z = coord
        x, y, z = float(x), float(y), float(z)
        for (dx, dy, dz) in vecs:
            v.addArrow({"start": {"x":x, "y":y, "z":z}, "end": {"x": x + float(dx), "y": y +float(dy), "z": z +float(dz)}, 'radius': 0.04, 'mid':0.95, 'color': color})
    v.setBackgroundColor('rgb(0,0,0)', 0)
    v.zoomTo()
    return v


def softmax(x):
    x = x - np.max(x, axis=-1, keepdims=True)
    y = np.exp(x)
    f_x = y / np.sum(y, axis=-1, keepdims=True)
    return f_x


def draw_backbone(datum: ProteinDatum, color="black", size=7, line_size=4, window=None):
    coord = datum.atom_coord
    res = datum.residue_token
    if window != None:
        coord = coord[window[0] : window[1]]
        res = res[window[0] : window[1]]

    x, y, z = coord[res != 0, 1, :].T
    data = [
        go.Scatter3d(
            name="backbone",
            x=x,
            y=y,
            z=z,
            marker=dict(
                size=size,
                colorscale="Viridis",
            ),
            hovertemplate="<b>%{text}</b><extra></extra>",
            text=np.arange(0, len(coord)),
            line=dict(color=color, width=line_size),
        )
    ]
    return data


def draw_bonds(
    datum: ProteinDatum,
    color: str = "black",
    size: float = 3.0,
    bond_size: float = 3.0,
):
    if not hasattr(datum, "bonds_list"):
        datum = DescribeChemistry().transform(datum)
    atom_coord = datum.atom_coord

    residue_flatten = lambda arr: rearrange(arr, "r a ... -> (r a) ...")

    bonds_list = residue_flatten(datum.bonds_list)
    bonds_mask = residue_flatten(datum.bonds_mask)
    bonds_list = bonds_list[bonds_mask.astype(np.bool_)].astype(np.int32)
    atom_coord = residue_flatten(datum.atom_coord)

    bonds_coords = []
    for v, u in bonds_list:
        bonds_coords.extend([atom_coord[v], atom_coord[u], [None, None, None]])
    bonds_coords = np.array(bonds_coords)
    x, y, z = bonds_coords.T
    data = [
        go.Scatter3d(
            name="bonds",
            x=x,
            y=y,
            z=z,
            marker=dict(size=size),
            line=dict(
                color=color,
                width=bond_size,
            ),
        ),
    ]
    return data


KELLY = [
    "#f2f3f4",
    "#222222",
    "#f3c300",
    "#875692",
    "#f38400",
    "#a1caf1",
    "#be0032",
    "#c2b280",
    "#848482",
    "#008856",
    "#e68fac",
    "#0067a5",
    "#f99379",
    "#604e97",
    "#f6a600",
    "#b3446c",
    "#dcd300",
    "#882d17",
    "#8db600",
    "#654522",
    "#e25822",
    "#2b3d26",
]


def draw_logits(logits: np.ndarray):
    (res_logits, sos_logits, eos_logits) = logits
    # residue_tokens = res_logits.argmax(-1)

    residue_data = []
    for (scores, res_name, color) in zip(softmax(res_logits).T, all_residues, KELLY):
        residue_data.append(
            go.Bar(
                name=res_name, x=np.arange(0, len(scores)), y=scores, marker_color=color
            )
        )

    sos_probs, eos_probs = softmax(sos_logits), softmax(eos_logits)
    sos = sos_logits.argmax(-1)
    eos = eos_logits.argmax(-1)
    boundary_data = [
        go.Scatter(
            x=np.arange(len(sos_probs)),
            y=sos_probs,
            mode="lines",
            line=dict(color="green"),
        ),
        go.Scatter(
            x=np.arange(len(eos_probs)),
            y=eos_probs,
            mode="lines",
            line=dict(color="red"),
        ),
    ]
    data = boundary_data + residue_data
    return data, sos, eos


def sos_eos_cut(model_output):
    (_, sos_logits, eos_logits) = model_output.logits
    datum = model_output.datum
    sos = sos_logits.argmax(-1)
    eos = eos_logits.argmax(-1)
    datum.atom_coord = datum.atom_coord[sos:eos]
    datum.residue_token = datum.residue_token[sos:eos]
    datum.residue_index = datum.residue_index[sos:eos]
    return datum


def _scatter(name, ca_coord, atom_coord, atom_mask, color, visible=True):
    sc_coords = []
    for ca, atoms, mask in zip(ca_coord, atom_coord, atom_mask):
        for atom in atoms[mask]:
            sc_coords.append(ca)
            sc_coords.append(atom)
            sc_coords.append([None, None, None])

    sc_coords = np.array(sc_coords)
    bb_x, bb_y, bb_z = ca_coord.T
    sc_x, sc_y, sc_z = sc_coords.T

    data = [
        go.Scatter3d(
            name=name + " coord",
            x=bb_x,
            y=bb_y,
            z=bb_z,
            marker=dict(
                size=7,
                colorscale="Viridis",
            ),
            line=dict(color=color, width=4),
            visible="legendonly" if not visible else True,
        ),
        go.Scatter3d(
            name=name + " vecs",
        x=sc_x,
            y=sc_y,
            z=sc_z,
            marker=dict(size=2, colorscale="Viridis"),
            line=dict(
                color=color,
                width=2,
            ),
            visible="legendonly",
        ),
    ]
    return data


# def draw_bonds(
#     name,
#     bonds_list,
#     atom_coord,
#     color,
#     atom_token: np.ndarray = None,
#     residue_token: np.ndarray = None,
#     visible=True,
# ):
#     bonds_coords, atom_names = [], []
#     bonds_list = bonds_list.astype(np.int32)
#     atom_coord = rearrange(atom_coord, "r a ... -> (r a) ...")
#     atom_token = rearrange(atom_token, "r a ... -> (r a) ...").astype(np.int32)
#     for v, u in bonds_list:
#         atom_names.extend([all_atoms[atom_token[v]], all_atoms[atom_token[u]], None])
#         bonds_coords.extend([atom_coord[v], atom_coord[u], [None, None, None]])
#     bonds_coords = np.array(bonds_coords)
#     x, y, z = bonds_coords.T
#     data = [
#         go.Scatter3d(
#             name=name + " bonds",
#             x=x,
#             y=y,
#             z=z,
#             hovertemplate="<b>%{text}</b><extra></extra>",
#             text=atom_names,
#             marker=dict(size=3),
#             line=dict(
#                 color=color,
#                 width=3,
#             ),
#         ),
#     ]
#     return data


def plot_3d(
    ground: ProteinDatum,
    hiddens,
    output: ProteinDatum,
    output_mask=None,
    width=650,
    height=650,
):
    scatters = []
    if ground is not None:
        scatters.extend(draw_bonds(ground, color="green"))

        scatters.extend(
            _scatter(
                "ground",
                ground.atom_coord[..., 1, :],
                ground.atom_coord,
                ground.atom_mask,
                "green",
                visible=False,
            )
        )

    for idx, internal in enumerate(hiddens):
        tent_coord = internal.irreps_array.filtered("1e").array
        atom_coord = internal.coord[..., None, :] + rearrange(
            tent_coord, "... (h c) -> ... h c", c=3
        )
        scatters.extend(
            _scatter(
                f"hidden {idx}",
                np.array(internal.coord),
                np.array(atom_coord),
                np.ones(atom_coord.shape[:-1]).astype(np.bool_),
                "blue",
                visible=False,
            )
        )

    if ground is not None:
        output_mask = output_mask if output_mask is not None else ground.atom_mask
        scatters.extend(
            _scatter(
                "output",
                output.atom_coord[..., 1, :],
                output.atom_coord,
                output_mask,
                "red",
                visible=False,
            )
        )

        if ground.bonds_mask is not None:
            scatters.extend(draw_bonds(output, color="red"))

    fig = go.Figure(data=scatters)
    fig.update_layout(
        autosize=False,
        width=width,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)

    return fig


def plot_series(series, name, log=False):
    fig = go.Figure()
    x = np.arange(len(series))
    if log:
        series = series + (0 - np.min(series))
    fig.add_trace(go.Scatter(x=x, y=series, name=name, line_shape="linear"))
    fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        width=650,
        height=400,
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="LightGray",
    )
    if log:
        fig.update_yaxes(type="log")

    return fig


def plot_samples(ground, latents, samples):
    scatters = draw_bonds(
        "ground",
        ground.bonds_list[ground.bonds_mask],
        ground.atom_coord,
        "green",
        ground.atom_token,
    )

    for idx, (latent, sample) in enumerate(zip(latents, samples)):
        tent_coord = latent.irreps_array.filtered("1e").array
        atom_coord = latent.coord[..., None, :] + rearrange(
            tent_coord, "... (h c) -> ... h c", c=3
        )
        scatters.extend(
            _scatter(
                f"hidden {idx}",
                np.array(latent.coord),
                np.array(atom_coord),
                np.ones(atom_coord.shape[:-1]).astype(np.bool_),
                "blue",
                visible=False,
            )
        )

        scatters.extend(
            draw_bonds(
                f"sample {idx}",
                ground.bonds_list[ground.bonds_mask],
                sample,
                "cyan",
                ground.atom_token,
            )
        )

    fig = go.Figure(data=scatters)
    fig.update_layout(
        autosize=False,
        width=650,
        height=650,
    )

    return fig

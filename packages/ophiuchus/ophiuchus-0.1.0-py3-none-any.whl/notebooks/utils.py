import os
import jax.numpy as jnp
import jax
from einops import rearrange, repeat
from moleculib.protein.alphabet import all_atoms, all_residues
import plotly.graph_objects as go
import numpy as np
from colour import Color


def to_pdb(batch):
    # indices for pdb writing were found in
    # https://colab.research.google.com/github/pb3lab/ibm3202/blob/
    # master/tutorials/lab02_molviz.ipynb#scrollTo=FPS04wJf5k3f
    atom_mask = batch.atom_mask[0].astype(jnp.bool_)
    
    all_atom_coords = batch.atom_coord[0][atom_mask]
    all_atom_tokens = batch.atom_token[0][atom_mask]
    all_atom_res_tokens = repeat(batch.residue_token[0], "r -> r a", a=14)[atom_mask]
    all_atom_res_indices = repeat(batch.residue_index[0], "r -> r a", a=14)[atom_mask]

    lines = []
    for idx, (coord, token, res_token, res_index) in enumerate(
        zip(
            all_atom_coords,
            all_atom_tokens,
            all_atom_res_tokens,
            all_atom_res_indices,
        )
    ):
        name = all_atoms[int(token)]
        res_name = all_residues[int(res_token)]
        x, y, z = coord
        line = list(" " * 80)
        line[0:6] = "ATOM".ljust(6)
        line[6:11] = str(idx + 1).ljust(5)
        line[12:16] = name.ljust(4)
        line[17:20] = res_name.ljust(3)
        line[22:26] = str(res_index + 1).ljust(4)
        line[30:38] = f"{x:.3f}".rjust(8)
        line[38:46] = f"{y:.3f}".rjust(8)
        line[46:54] = f"{z:.3f}".rjust(8)
        line[76:78] = name[0].rjust(2)
        lines.append("".join(line))
    lines = "\n".join(lines)
    return lines


def align_latents(l1, l2):
    rotations = jax.vmap(jax.vmap(rigid_Kabsch_3D, in_axes=(0, 0)))(
        l1.filter("1e").array, l2.filter("1e").array
    )

    rotations = jax.lax.stop_gradient(rotations)  # do we need this?

    aligned_l1 = jax.vmap(
        jax.vmap(lambda r, q: q.transform_by_matrix(r), in_axes=(0, 0))
    )(rotations, l1)

    return aligned_l1


def _scatter(name, coord, mask, color="blue"):
    x, y, z = coord[0].T
    x = [x for x in x if x != 0.0]
    y = [x for x in y if x != 0.0]
    z = [x for x in z if x != 0.0]

    data = [
        go.Scatter3d(
            name=name,
            x=x,
            y=y,
            z=z,
            marker=dict(size=5, colorscale="Viridis"),
            line=dict(color=color, width=2),
        ),
    ]
    return data


def _bonds(name, coord, bonds, bond_mask, color):
    coord, bonds, bond_mask = coord[0], bonds[0].astype(np.int32), bond_mask[0]

    bonds_coords = []

    for res_bonds, res_bonds_mask, res_coords in zip(bonds, bond_mask, coord):
        for m, (v, u) in zip(res_bonds_mask, res_bonds):
            if not m:
                continue

            vpos, upos = res_coords[v], res_coords[u]

            if vpos.sum(-1) == 0.0 or upos.sum(-1) == 0.0:
                continue
            bonds_coords.extend([vpos, upos, [None, None, None]])

    bonds_coords = np.array(bonds_coords)
    x, y, z = bonds_coords.T
    data = [
        go.Scatter3d(
            name=name + " bonds",
            x=x,
            y=y,
            z=z,
            marker=dict(size=2),
            line=dict(
                color=color,
                width=3,
            ),
        ),
    ]
    return data


# def rigid_Kabsch_3D(Q, P):
#     Q = rearrange(Q, "(d c) -> d c", c=3)
#     P = rearrange(P, "(d c) -> d c", c=3)
#     B = jnp.einsum("ji,jk->ik", Q, P)
#     U, S, Vh = jnp.linalg.svd(B)
#     R = jnp.matmul(Vh.T, U.T)
#     d = jnp.sign(jnp.linalg.det(R))
#     return jax.lax.cond(
#         d < 0,
#         lambda _: jnp.matmul(
#             jnp.matmul(
#                 Vh.T,
#                 jnp.diag(jnp.array([1, 1, d])),
#             ),
#             U.T,
#         ),
#         lambda _: R,
#         None,
#     )

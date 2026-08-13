from cluster.hash_ring import HashRing


nodes = ["node1", "node2", "node3"]

ring = HashRing(nodes)


print("Hash ring created")

for key in ["foo", "bar", "user:1", "user:2", "school", "name"]:
    node = ring.get_node(key)
    print(f"{key} -> {node}")
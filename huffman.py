# coding: utf-8

from binary_tree import *


class Huffman(BinaryTree):
    """ This class is an implementation of the Huffman compression algorithm.

    Attributes
    ----------
    bytes_occurrences : dict
        Association between a byte and its number occurrences.

    huffman_code : dict
        Association between a byte and its new code.

    traversal_values : list
        Stores results of a traversal.

    Notes
    -----
    The method we have chosen to use here is semi-adaptive because it will build a tree based on actual frequencies
    instead of using static symbols weights.
    (but it will not dynamically change the tree like the real adaptive algorithm
    https://en.wikipedia.org/wiki/Adaptive_Huffman_coding ).
    The problem with this method is that we have to transmit the tree with the encoded content in order to decompress.
    The tree can't be bigger than 256 leaves, which means this method will be good to compress big chunks of data but
    it will be inefficient to compress small ones.
    """

    def __init__(self):
        super().__init__()
        self.bytes_occurrences = {}
        self.huffman_code = {}
        self.traversal_values = []

    def create_node_from_children(self, left, right):
        """ Redefine parent's behavior.

        Notes
        -----
        Our algorithm only cares about tree leaves but we need the tree to be built depending on bytes occurrences,
        that why newly created node's value will be an addition of children sort_on values (which are in this algorithm
        byte occurrences).
        """

        new_node = Node(left.sort_on + right.sort_on)
        new_node.left = left
        new_node.right = right
        return new_node

    def __find_bytes_occurrences(self, bytes_list):

        # Count bytes
        for byte in bytes_list:
            try:
                self.bytes_occurrences[byte] += 1
            except KeyError:
                self.bytes_occurrences[byte] = 1

    def __create_huffman_code(self, node, code=""):

        if node.is_leaf():
            self.huffman_code[node.value] = code

        else:
            self.__create_huffman_code(node.left, code + "0")
            self.__create_huffman_code(node.right, code + "1")

    def __compress(self, bytes_list):

        self.__find_bytes_occurrences(bytes_list)
        print("Occurrences: " + str(self.bytes_occurrences))
        print("Number of different bytes : {}".format(len(self.bytes_occurrences)))

        tree_values = []

        for byte in self.bytes_occurrences:
            new_node = Node(byte)  # Leaf
            new_node.sort_on = self.bytes_occurrences[byte]  # Nodes will be sorted by bytes occurrences
            tree_values.append(new_node)

        self.build_tree(tree_values)

        print("Tree: " + str(self.root_node))
        self.__create_huffman_code(self.root_node)
        print("Code: " + str(self.huffman_code))

        encoded_string = "1"  # Padding needed to convert to bytes, otherwise we will lose information (the first zeros)

        for byte in bytes_list:
            encoded_string += self.huffman_code[byte]

        print("Encoded: " + encoded_string)

        # Convert to bytes array
        return int(encoded_string, 2).to_bytes((len(encoded_string)+7) // 8, byteorder='big')

    def traversal_action(self, node):
        """Overwrites BinaryTree's default action.

        Parameters
        ----------
        node : Node
            The node to process.
        """
        value = node.value

        # If the node isn't a leaf, the node is represented as a 0 (it's ok to rebuild the tree).
        if not node.is_leaf():
            value = 0

        self.traversal_values.append(value)

    def compress_file(self, input_filename, output_filename):
        print("Reading {}...".format(input_filename))

        with open(input_filename, "rb") as input_file:
            bytes_list = input_file.read()  # All the file will be in memory, can be a problem with huge files.

        print("Input size : ", len(bytes_list))
        compressed = self.__compress(bytes_list)
        print("Compressed size : ", len(compressed))

        # Find inorder and preorder sequences of the tree, thanks to these values, we'll be able to rebuild the tree.
        # Each integers will be stored on 1 byte, and the first integer will be the number of bytes (minus one because
        # we byte 256 doesn't exist
        to_store_in_the_file = [len(self.bytes_occurrences)-1]

        self.traversal_values.clear()
        self.inorder_traversal()
        to_store_in_the_file += self.traversal_values

        self.traversal_values.clear()
        self.preorder_traversal()
        to_store_in_the_file += self.traversal_values

        to_store_in_the_file = bytes(to_store_in_the_file)
        total_file_size = len(to_store_in_the_file) + len(compressed)

        print("Total size output : {} bytes".format(total_file_size))

        if len(bytes_list) <= total_file_size:
            raise Exception("Aborted. No gain, you shouldn't compress that file. (+{} bytes)".format(total_file_size-len(bytes_list)))

        print("Compression gain : {0:.2f}%".format(100-total_file_size * 100 / len(bytes_list)))

        with open(output_filename, "wb") as output_file:
            output_file.write(to_store_in_the_file)
            output_file.write(compressed)

    def decompress_file(self, input_filename, output_filename):
        # int.from_bytes(compressed, byteorder='big')
        pass

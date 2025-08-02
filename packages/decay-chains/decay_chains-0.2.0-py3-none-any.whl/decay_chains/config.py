import math
import xml.etree.ElementTree as et
from typing import Literal
from treelib.tree import Tree
from importlib import resources

class Config:
    """
    A configuration object used to provide data to the DecayChain calculator.
    After creating a config object and adding chain information, it can be used
    to instantiate a DecayChain using ```chain = DecayChain(config)```.
    """
    _sources = {}
    _initial_quantities = {}
    decay_info = {}
    atom_numbers = {}
    sources = {}
    
    def add_nuclide_number(self, nuclide: str, number: float):
        """
        Adds a quantity of nuclide atoms.
        
        Parameters
        ----------
        nuclide : str
            The nuclide identifier. Ex. U238.
        number : float
            The initial number of atoms in the sample
        """
        self._initial_quantities[nuclide] = (number, "number")
    
    def add_nuclide_activity(self, nuclide: str, activity: float, units:
                             Literal["Bq", "Ci"] = "Bq"):
        """
        Adds an activity of nuclide.

        Parameters
        ----------
        nuclide : str
            The nuclide identifier. Ex. U238.
        activity : float
            The initial activity of the sample in either Bq or Ci.
        units: "Bq" or "Ci"
            The units of the supplied activity (default is Bq).
        """
        if (units == "Ci"):
            activity *= 37e9
        self._initial_quantities[nuclide] = (activity, "activity")

    def add_from_xml(self, input_file: str = "input.xml"):
        """
        Fills configuration with data from an xml input.

        Parameters
        ----------
        input_file : str
            The filename of the xml input.
        """
        # Parse the input file
        isotopes_xml = et.parse(input_file).getroot().findall('nuclide')
        for nuclide in isotopes_xml:
            info = nuclide.attrib
            self._initial_quantities[info['name']] = \
                (float(info['N0']), "number")
            self.sources[info['name']] = float(info['source'])

    def add_from_parent(self, nuclide: str, quantity: float, units:
                        Literal["number", "Bq", "Ci"], depth: int):
        """
        Adds all nuclides in a chain depth nuclides deep starting with nuclide.
        All children of the starting nuclide are initialized with zero atoms.
        The parent is initialized with a quantity, given in atoms, Bq, or Ci.

        Paramters
        ---------
        nuclide : str
            The parent nuclide identifier. Ex. U238.
        quantity : float
            The initial quantity of the parent nuclide in either atoms, Bq, or
            Ci.
        units: "number" or "Bq" or "Ci"
            The units of the supplied quantity.
        depth : int
            The depth of the chain to create.
        """
        tree = Config._create_tree(nuclide, depth)
        nuclides = [nuc.tag for nuc in tree.all_nodes()]
        nuclides = list(set(nuclides))
        multiplier = 1.
        final_unit = ""
        if units == "Ci":
            final_unit = "activity"
            multiplier = 37e9
        if units == "Bq":
            final_unit = "activity"
        for nuc in nuclides:
            if nuc == nuclide:
                self._initial_quantities[nuc] = (quantity * multiplier, final_unit)
                continue
            self._initial_quantities[nuc] = (0., "number")

    def configure(self):
        """
        Performs calculations and conversions to prepare object for use in the
        decay calculator.
        """
        chain_file = resources.path("decay_chains", "chain_endfb71_pwr.xml")
        with chain_file as f:
            chain = et.parse(f).getroot().findall('nuclide')

        atom_numbers = {}
        for nuclide in chain:
            info = nuclide.attrib
            el = info['name']
            if el in self._initial_quantities.keys():
                print(f'Reading data for {el} from chain file')
                # Need error handling if nuclide is stable
                try:
                    self.decay_info[el] = \
                        {'half_life': float(info['half_life'])}
                    self.decay_info[el]['decay_const'] = \
                        math.log(2) / float(info['half_life'])
                except KeyError:
                    self.decay_info[el] = {'half_life': 0.}
                    # If stable, set lambda to 0 so there is no decay
                    self.decay_info[el]['decay_const'] = 0.
                    
                # Add initial atom number to dictionary
                atom_numbers[el] = self._initial_quantities[el][0]
                if (self._initial_quantities[el][1] == "activity"):
                    if (self.decay_info[el]['decay_const'] == 0. and
                        atom_numbers[el] != 0.):
                        
                        print(f"\nWARNING: {el} is stable! Ignoring activity "
                               "and setting number to zero.")
                        atom_numbers[el] = 0.
                    else:
                        atom_numbers[el] /= self.decay_info[el]['decay_const']
                # Find the decay targets
                self.decay_info[el]['targets'] = {}
                for mode in nuclide.findall('decay'):
                    m = mode.attrib
                    # Do not include spontaneous fission
                    if m['type'] == "sf":
                        print(f"\nWARNING: Ignoring spontaneous fission in {el} "
                              f"({float(m['branching_ratio']) * 100:.4e}%).\n")
                    else:
                        self.decay_info[el]['targets'][m['target']] = \
                            float(m['branching_ratio'])
                        
        for nuc in self.decay_info.keys():
            self.atom_numbers[nuc] = [atom_numbers[nuc]]

        # Fill in the nuclides
        for nuc, info in self.decay_info.items():
            self.decay_info[nuc]["parents"] = []
            for pnuc, pinfo in self.decay_info.items():
                if nuc in pinfo["targets"].keys():
                    self.decay_info[nuc]["parents"].append(pnuc)
        
        # If source was not set, set it to 0
        for el in self.decay_info.keys():
            if el not in self.sources.keys():
                self.sources[el] = 0.

    @staticmethod
    def _create_tree(parent: str, depth: int = 5,
                   _tree: Tree | None = None, _id: int = 0) -> Tree:
        """
        Draws the decay chain from a starting parent isotope.
        
        Parameters
        ----------
        parent : str
            The parent nuclide to start from. Must be of the form U235.
        depth : int
            The depth of the decay tree (default is 5).
        tree : Tree or None
            The working decay tree. Not needed by user (default is None).
        id : int
            The id of the parent isotope in the tree. Not needed by user
            (default is 0).

        Returns
        -------
        Tree
            The populated tree containing the decay chain.
        """
        if _tree is None:
            _tree = Tree()
        depth -= 1
        if depth <= 0:
            return _tree
        # This makes LSP happy, it can't recognize tree is not None otherwise
        tree: Tree = _tree
        
        chain_file = resources.path("decay_chains", "chain_endfb71_pwr.xml")
        with chain_file as f:
            chain = et.parse(f).getroot().findall('nuclide')
        for nuclide in chain:
            info = nuclide.attrib
            el = info['name']
            if el == parent:
                if tree.depth() == 0:
                    _id = tree.size()
                    tree.create_node(el, el + str(_id))
                for mode in nuclide.findall('decay'):
                    m = mode.attrib
                    child = m['target']
                    if m['type'] == "sf":
                        child = "Spontaneous fission"
                    cid = tree.size()
                    tree.create_node(child, child + str(cid),
                                      parent = el + str(_id))
                    tree = Config._create_tree(child, depth, tree, cid)
                return tree
        # This makes the LSP happy, even though the code never gets here
        return tree
        
    @staticmethod
    def draw_chain(parent: str, depth: int = 5):
        tree = Config._create_tree(parent, depth)
        tree.show()

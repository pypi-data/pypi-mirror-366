"""
Unit and regression test for the pairk package.
"""

# Import package, test suite, and other packages as needed
import sys
import pytest

import a3mcat
import a3mcat.examples as examples

def test_a3mcat_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "a3mcat" in sys.modules

# # import an a3m file
# msa = a3mcat.MSAa3m.from_a3m_file(examples.a3m_file1)
# print(msa)

# # slicing the alignment
# print(msa[2:5])

# # concatenating alignments
# msa2 = a3mcat.MSAa3m.from_a3m_file(examples.a3m_file2)
# print(msa2)
# print(msa + msa2)
# print(msa + msa2 + msa)

# # saving the alignment
# # msa[2:5].save("test_alignment_1_sliced.a3m")
# Copyright 2023-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Mathematical special functions, abstract and concrete.

**boring_math.special_functions.abstract**

+-----------+---------------------------+---------------------+
| Function  | Description               | Type                |
+===========+===========================+=====================+
| ``const`` | Constant function factory | ``T -> [[T] -> T]`` |
+-----------+---------------------------+---------------------+
| ``id``    | Identity function         | ``T -> T``          |
+-----------+---------------------------+---------------------+

----

**boring_math.special_functions.float**

+------------+----------------------+
| Function   | Description          |
+==========+=================+======+
| ``exp(z)`` | exponential function |
+------------+----------------------+
| ``sin(z)`` | sine function        |
+------------+----------------------+

----

**boring_math.special_functions.complex**

+------------+----------------------+
| Function   | Description          |
+============+=================+====+
| ``exp(z)`` | exponential function |
+------------+----------------------+
| ``sin(z)`` | sine function        |
+------------+----------------------+

"""

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'

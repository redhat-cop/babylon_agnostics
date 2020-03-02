# Copyright: (c) 2020, Johnathan Kupferer <jkupfere@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: relative_vars
    author: Johnathan Kupferer <jkupfere@redhat.com>
    version_added: "2.9"
    short_description: resolve template from string
    description:
      - Return evaluated template
    options:
      _terms:
        description: list of template strings
"""

EXAMPLES = """
- name: show templating results
  debug:
    msg: "{{ lookup('relative_vars', 'foo', context_vars=bar)}}"
"""

RETURN = """
_raw:
   description: templated string
"""

from ansible.plugins.lookup import LookupBase
from copy import deepcopy
from six import string_types
import pprint

class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        convert_data_p = kwargs.get('convert_data', True)
        context_vars = kwargs.get('context_vars', {})
        ret = []

        if isinstance(context_vars, string_types):
            context_vars = self._templar.template(
                context_vars, preserve_trailing_newlines=False,
                convert_data=True, escape_backslashes=False
            )

        variable_start_string = kwargs.get('variable_start_string', None)
        variable_end_string = kwargs.get('variable_end_string', None)

        old_vars = self._templar.available_variables
        if variable_start_string is not None:
            self._templar.environment.variable_start_string = variable_start_string
        if variable_end_string is not None:
            self._templar.environment.variable_end_string = variable_end_string

        # The template will have access to all existing variables,
        # plus some added by ansible (e.g., template_{path,mtime}),
        # plus anything passed to the lookup with the template_vars=
        # argument.
        myvars = deepcopy(variables)
        myvars.update(context_vars)
        self._templar.available_variables = myvars

        for term in terms:
            # do the templating
            res = self._templar.template(
                '{{' + term + '}}', preserve_trailing_newlines=True,
                convert_data=convert_data_p, escape_backslashes=False
            )

            ret.append(res)

        # restore old variables
        self._templar.available_variables = old_vars

        return ret

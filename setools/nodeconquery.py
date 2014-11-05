# Copyright 2014, Tresys Technology, LLC
#
# This file is part of SETools.
#
# SETools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 2.1 of
# the License, or (at your option) any later version.
#
# SETools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with SETools.  If not, see
# <http://www.gnu.org/licenses/>.
#
try:
    import ipaddress
except ImportError:
    pass

import re

from . import compquery
from . import contextquery


class NodeconQuery(contextquery.ContextQuery):

    """Nodecon query."""

    def __init__(self, policy,
                 net="", net_overlap=False,
                 user="", user_regex=False,
                 role="", role_regex=False,
                 type_="", type_regex=False,
                 range_=""):
        """
        Parameters:
        policy          The policy to query.

        net             The network address.
        overlap         If true, the net will match if it overlaps with
                        the nodecon's network instead of equality.
        user            The criteria to match the context's user.
        user_regex      If true, regular expression matching
                        will be used on the user.
        role            The criteria to match the context's role.
        role_regex      If true, regular expression matching
                        will be used on the role.
        type_           The criteria to match the context's type.
        type_regex      If true, regular expression matching
                        will be used on the type.
        range_          The criteria to match the context's range.
        """

        self.policy = policy

        self.set_network(net, overlap=net_overlap)
        self.set_user(user, regex=user_regex)
        self.set_role(role, regex=role_regex)
        self.set_type(type_, regex=type_regex)
        self.set_range(range_)

    def results(self):
        """Generator which yields all matching genfscons."""

        for n in self.policy.nodecons():

            if self.network:
                try:
                    net = ipaddress.ip_network(
                        '{0.address}/{0.netmask}'.format(n))
                except NameError:
                    # Should never actually hit this since the self.network
                    # setter raises the same exception.
                    raise RuntimeError(
                        "IP address/network functions require Python 3.3+.")

                if self.network_overlap:
                    if not self.network.overlaps(net):
                        continue
                else:
                    if not net == self.network:
                        continue

            if not self._match_context(
                    n.context,
                    self.user,
                    self.user_regex,
                    self.user_cmp,
                    self.role,
                    self.role_regex,
                    self.role_cmp,
                    self.type_,
                    self.type_regex,
                    self.type_cmp,
                    self.range_):
                continue

            yield n

    def set_network(self, net, **opts):
        """
        Set the criteria for matching the network.

        Parameter:
        net         String IPv4/IPv6 address or IPv4/IPv6 network address
                    with netmask, e.g. 192.168.1.0/255.255.255.0 or
                    "192.168.1.0/24".

        Keyword parameters:
        overlap     If true, the criteria will match if it overlaps with the
                    nodecon's network instead of equality.

        Exceptions:
        NameError   Invalid keyword parameter.
        """

        if net:
            try:
                self.network = ipaddress.ip_network(net)
            except NameError:
                raise RuntimeError(
                    "IP address/network functions require Python 3.3+.")
        else:
            # ensure self.network is set
            self.network = None

        for k in list(opts.keys()):
            if k == "overlap":
                self.network_overlap = opts[k]
            else:
                raise NameError("Invalid name option: {0}".format(k))
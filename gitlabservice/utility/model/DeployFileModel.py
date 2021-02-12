from collections import namedtuple

DeployFileHeader = namedtuple('deploy', 'group profile')
DeployFileObject = namedtuple('object', 'name type action')
DeployFileParam = namedtuple('param', 'name type base')

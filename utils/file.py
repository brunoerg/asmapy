import sys
from asmap import ASMap, net_to_prefix, prefix_to_net
import ipaddress

def load_file(input_file, state=None):
    try:
        contents = input_file.read()
    except OSError as err:
        sys.exit("Input file '%s' cannot be read: %s." % (input_file.name, err.strerror))
    try:
        bin_asmap = ASMap.from_binary(contents)
    except ValueError:
        bin_asmap = None
    txt_error = None
    entries = None
    try:
        txt_contents = str(contents, encoding="utf-8")
    except UnicodeError:
        txt_error = "invalid UTF-8"
        txt_contents = None
    if txt_contents is not None:
        entries = []
        for line in txt_contents.split("\n"):
            idx = line.find('#')
            if idx >= 0:
                line = line[:idx]
            line = line.lstrip(' ').rstrip(' \t\r\n')
            if len(line) == 0:
                continue
            fields = line.split(' ')
            if len(fields) != 2:
                txt_error = "unparseable line '%s'" % line
                entries = None
                break
            prefix, asn = fields
            if len(asn) <= 2 or asn[:2] != "AS" or any(c < '0' or c > '9' for c in asn[2:]):
                txt_error = "invalid ASN '%s'" % asn
                entries = None
                break
            try:
                net = ipaddress.ip_network(prefix)
            except ValueError:
                txt_error = "invalid network '%s'" % prefix
                entries = None
                break
            entries.append((net_to_prefix(net), int(asn[2:])))
    if entries is not None and bin_asmap is not None and len(contents) > 0:
        sys.exit("Input file '%s' is ambiguous." % input_file.name)
    if entries is not None:
        if state is None:
            state = ASMap()
        state.update_multi(entries)
        return state
    if bin_asmap is not None:
        if state is None:
            return bin_asmap
        sys.exit("Input file '%s' is binary, and cannot be applied as a patch." % input_file.name)
    sys.exit("Input file '%s' is neither a valid binary asmap file nor valid text input (%s)." % (input_file.name, txt_error))


def save_binary(output_file, state, fill):
    contents = state.to_binary(fill=fill)
    try:
        output_file.write(contents)
        output_file.close()
    except OSError as err:
        sys.exit("Output file '%s' cannot be written to: %s." % (output_file.name, err.strerror))

def save_text(output_file, state, fill, overlapping):
    for prefix, asn in state.to_entries(fill=fill, overlapping=overlapping):
        net = prefix_to_net(prefix)
        try:
            print("%s AS%i" % (net, asn), file=output_file)
        except OSError as err:
            sys.exit("Output file '%s' cannot be written to: %s." % (output_file.name, err.strerror))
    try:
        output_file.close()
    except OSError as err:
        sys.exit("Output file '%s' cannot be written to: %s." % (output_file.name, err.strerror))
def cut_str(string: str, scope_width: int, separator: str = "...") -> str:
    if scope_width == -1:
        return string
    else:
        if len(string) <= scope_width:
            return string

        scope_width -= len(separator)
        return string[:scope_width // 2] + separator + string[-scope_width // 2:]


def cut_lines_len_in_multiline_string(input_str: str, scope_width: int) -> str:
    strs = input_str.split('\n')
    output_list = [cut_str(item, scope_width) for item in strs]
    return '\n'.join(output_list)

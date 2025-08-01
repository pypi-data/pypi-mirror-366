def get_short_type(value):
    type_map = {
        int  : 'd',
        float: 'f',
        str  : 's',
        bool : 'b',
        list : 'l',
        dict : 'm',
        tuple: 't',
        set  : 'set'}

    return type_map.get(type(value), 'u')
        

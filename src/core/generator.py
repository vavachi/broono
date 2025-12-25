import re

class ScriptGenerator:
    def generate(self, diff):
        script_parts = []
        
        # 1. Tables
        table_diff = diff['tables']
        for table_name, table_def in table_diff['new'].items():
            script_parts.append(self._generate_create_table(table_name, table_def))
            
        for table_name, changes in table_diff['modified'].items():
            for col_name, col_def in changes['add_columns'].items():
                script_parts.append(self._generate_add_column(table_name, col_name, col_def))
            for col_name, col_def in changes['alter_columns'].items():
                script_parts.append(self._generate_alter_column(table_name, col_name, col_def))
            for col_name in changes['drop_columns']:
                script_parts.append(self._generate_drop_column(table_name, col_name))
                
        for table_name in table_diff['dropped']:
            script_parts.append(f"-- DROP TABLE {table_name};\n")

        # 2. Stored Objects (Procs, Funcs, Triggers)
        for obj_type in ['procedures', 'functions', 'triggers']:
            obj_diff = diff[obj_type]
            
            # New or Modified
            for name, obj_def in obj_diff['new'].items():
                script_parts.append(f"-- NEW {obj_type.upper()}: {name}")
                script_parts.append(obj_def['definition'] + "\nGO\n")
                
            for name, obj_def in obj_diff['modified'].items():
                script_parts.append(f"-- MODIFY {obj_type.upper()}: {name}")
                alt_def = self._make_alter(obj_def['definition'])
                script_parts.append(alt_def + "\nGO\n")

            for name in obj_diff['dropped']:
                script_parts.append(f"-- DROP {obj_type[:-1].upper()}: {name};\n")

        return "\n".join(script_parts)

    def _make_alter(self, definition):
        # Very simple replacement for the first occurrence of CREATE with ALTER
        return re.sub(r'\bCREATE\b', 'ALTER', definition, count=1, flags=re.IGNORECASE)

    def _generate_create_table(self, table_name, table_def):
        lines = [f"CREATE TABLE {table_name} ("]
        cols = []
        for col_name, col_def in table_def['columns'].items():
            cols.append("    " + self._def_string(col_name, col_def))
        lines.append(",\n".join(cols))
        lines.append(");\nGO\n")
        return "\n".join(lines)

    def _generate_add_column(self, table_name, col_name, col_def):
        return f"ALTER TABLE {table_name} ADD {self._def_string(col_name, col_def)};\nGO\n"

    def _generate_alter_column(self, table_name, col_name, col_def):
        return f"ALTER TABLE {table_name} ALTER COLUMN {self._def_string(col_name, col_def)};\nGO\n"

    def _generate_drop_column(self, table_name, col_name):
        return f"ALTER TABLE {table_name} DROP COLUMN {col_name};\nGO\n"

    def _def_string(self, col_name, col_def):
        base = f"[{col_name}] {col_def['type']}"
        
        type_lower = col_def['type'].lower()
        if type_lower in ['varchar', 'nvarchar', 'char', 'nchar', 'varbinary', 'binary']:
            length = col_def['length']
            if length == -1 or length == None:
                 if length == -1: base += "(MAX)"
            else:
                 base += f"({length})"
        elif type_lower in ['decimal', 'numeric']:
            prec = col_def['precision']
            scale = col_def['scale']
            if prec:
                base += f"({prec}, {scale})"

        if not col_def['nullable']:
            base += " NOT NULL"
        else:
            base += " NULL"
            
        return base

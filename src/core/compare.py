class SchemaComparer:
    def compare(self, source_schema, target_schema):
        """
        Compares source_schema against target_schema.
        """
        diff = {
            'tables': self._compare_object_type(source_schema['tables'], target_schema['tables'], is_table=True),
            'procedures': self._compare_object_type(source_schema['procedures'], target_schema['procedures']),
            'functions': self._compare_object_type(source_schema['functions'], target_schema['functions']),
            'triggers': self._compare_object_type(source_schema['triggers'], target_schema['triggers'])
        }
        return diff

    def _compare_object_type(self, source_objs, target_objs, is_table=False):
        type_diff = {
            'new': {},
            'dropped': [],
            'modified': {}
        }

        # 1. New Objects
        for name, obj_def in source_objs.items():
            if name not in target_objs:
                type_diff['new'][name] = obj_def

        # 2. Dropped Objects
        for name in target_objs:
            if name not in source_objs:
                type_diff['dropped'].append(name)

        # 3. Modified Objects
        for name, source_def in source_objs.items():
            if name in target_objs:
                target_def = target_objs[name]
                if is_table:
                    table_diff = self._compare_tables(source_def, target_def)
                    if table_diff:
                        type_diff['modified'][name] = table_diff
                else:
                    # Generic comparison for stored objects (by definition)
                    if source_def['definition'] != target_def['definition']:
                         type_diff['modified'][name] = source_def

        return type_diff

    def _compare_tables(self, source_table, target_table):
        changes = {
            'add_columns': {},
            'alter_columns': {},
            'drop_columns': []
        }
        
        source_cols = source_table['columns']
        target_cols = target_table['columns']

        # Check for Add Columns
        for col_name, col_def in source_cols.items():
            if col_name not in target_cols:
                changes['add_columns'][col_name] = col_def
            else:
                # Check for Alter Columns
                target_col_def = target_cols[col_name]
                if self._is_column_different(col_def, target_col_def):
                    changes['alter_columns'][col_name] = col_def

        # Check for Drop Columns
        for col_name in target_cols:
            if col_name not in source_cols:
                changes['drop_columns'].append(col_name)

        # Return changes if any, else None
        if changes['add_columns'] or changes['alter_columns'] or changes['drop_columns']:
            return changes
        return None

    def _is_column_different(self, source_col, target_col):
        # Compare extraction properties
        # type, nullable, length, precision, scale
        if source_col['type'] != target_col['type']:
            return True
        if source_col['nullable'] != target_col['nullable']:
            return True
        # Length, Precision, Scale comparison depends on type, but simple inequality is usually safe if extracted consistently
        # Note: None != 100, so be careful with None values if extraction defaults differ.
        # But SchemaExtractor should be consistent.
        if source_col['length'] != target_col['length']:
            return True
        if source_col['precision'] != target_col['precision']:
            return True
        if source_col['scale'] != target_col['scale']:
            return True
            
        return False

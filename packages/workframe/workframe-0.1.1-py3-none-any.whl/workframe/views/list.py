"""ListView class for paginated, mobile-optimized list views."""

from typing import List, Dict, Any, Optional
from flask import request, url_for, render_template_string, render_template, Response
from sqlalchemy import desc, asc
import csv
import io
from ..models.table import Table
from ..models.field import Field


class ListView:
    """
    ListView for displaying paginated, searchable, mobile-first data tables.
    
    Provides mobile-optimized list views with search, sorting, and pagination
    specifically designed for business applications.
    """
    
    def __init__(self, table: Table, per_page: int = 20):
        """
        Initialize ListView.
        
        Args:
            table: Table instance to display
            per_page: Number of records per page
        """
        self.table = table
        self.per_page = per_page
        self.search_query = ''
        self.sort_field = None
        self.sort_order = 'asc'
        self.page = 1
        
        # Get display fields (excluding hidden)
        self.display_fields = self._get_display_fields()
        self.searchable_fields = self._get_searchable_fields()
    
    def _get_display_fields(self) -> List[Field]:
        """Get fields that should be displayed in list view."""
        fields = []
        for field in self.table.fields:
            if not field.hidden and not field.hidden_in_list:
                fields.append(field)
        return fields[:6]  # Limit to 6 fields for mobile optimization
    
    def _get_searchable_fields(self) -> List[Field]:
        """Get fields that can be searched."""
        searchable_types = ['text', 'email', 'string', 'textarea']
        return [f for f in self.display_fields if f.type in searchable_types]
    
    def process_request_params(self):
        """Process request parameters for search, sort, and pagination."""
        # Search
        self.search_query = request.args.get('search', '').strip()
        
        # Sorting
        self.sort_field = request.args.get('sort', 'id')
        self.sort_order = request.args.get('order', 'desc')
        
        # Pagination
        try:
            self.page = int(request.args.get('page', 1))
        except (ValueError, TypeError):
            self.page = 1
        
        if self.page < 1:
            self.page = 1
    
    def get_query(self, filters: Optional[Dict[str, Any]] = None):
        """
        Build the base query with search, sorting, and optional custom filters.
        
        Args:
            filters: Optional dictionary of field_name -> value filters
        
        Returns:
            SQLAlchemy query object
        """
        if not self.table.model:
            raise ValueError("Table model not available")
        
        query = self.table.model.query
        
        # Apply custom filters first
        if filters:
            for field_name, filter_value in filters.items():
                column = getattr(self.table.model, field_name, None)
                if column and filter_value is not None:
                    query = query.filter(column == filter_value)
        
        # Apply search filter
        if self.search_query and self.searchable_fields:
            search_conditions = []
            for field in self.searchable_fields:
                column = getattr(self.table.model, field.name, None)
                if column:
                    search_conditions.append(
                        column.ilike(f'%{self.search_query}%')
                    )
            
            if search_conditions:
                from sqlalchemy import or_
                query = query.filter(or_(*search_conditions))
        
        # Apply sorting
        if self.sort_field:
            sort_column = getattr(self.table.model, self.sort_field, None)
            if sort_column:
                if self.sort_order == 'desc':
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        
        return query
    
    def get_paginated_results(self, filters: Optional[Dict[str, Any]] = None):
        """
        Get paginated results.
        
        Args:
            filters: Optional dictionary of field_name -> value filters
        
        Returns:
            Flask-SQLAlchemy pagination object
        """
        query = self.get_query(filters)
        return query.paginate(
            page=self.page,
            per_page=self.per_page,
            error_out=False
        )
    
    def get_data(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get list data as dictionary (useful for AJAX responses).
        
        Args:
            filters: Optional dictionary of field_name -> value filters
        
        Returns:
            Dictionary with records and metadata
        """
        # Process request parameters for search and sorting
        self.process_request_params()
        
        # Get paginated results with filters
        pagination = self.get_paginated_results(filters)
        
        # Format records for JSON response
        records = []
        for record in pagination.items:
            record_data = {'id': record.id}
            
            # Add field values
            for field in self.display_fields:
                value = getattr(record, field.name, None)
                
                # Handle lookup fields - get display value
                if field.is_lookup_field() and value:
                    try:
                        if hasattr(self.table, 'db') and self.table.db:
                            lookup_model = field._get_lookup_model(self.table.db)
                            if lookup_model:
                                lookup_record = self.table.db.session.query(lookup_model).filter_by(id=value).first()
                                if lookup_record:
                                    display_value = getattr(lookup_record, field.display, str(value))
                                    value = display_value
                    except Exception:
                        # If lookup fails, just use the raw value
                        pass
                
                # Format the value
                formatted_value = field.format_value(value) if value is not None else ''
                record_data[field.name] = formatted_value
            
            records.append(record_data)
        
        return {
            'records': records,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            },
            'display_fields': [{'name': f.name, 'title': f.name.replace('_', ' ').title()} for f in self.display_fields]
        }
    
    def get_sort_url(self, field_name: str) -> str:
        """
        Get URL for sorting by a field.
        
        Args:
            field_name: Name of field to sort by
            
        Returns:
            URL string for sorting
        """
        # Toggle sort order if already sorting by this field
        if self.sort_field == field_name:
            new_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            new_order = 'asc'
        
        params = {
            'sort': field_name,
            'order': new_order,
            'page': 1  # Reset to first page when sorting
        }
        
        # Preserve search query
        if self.search_query:
            params['search'] = self.search_query
        
        return url_for(request.endpoint, **params)
    
    def get_search_url(self) -> str:
        """Get URL for search form submission."""
        return url_for(request.endpoint)
    
    def get_page_url(self, page_num: int) -> str:
        """
        Get URL for a specific page.
        
        Args:
            page_num: Page number
            
        Returns:
            URL string for the page
        """
        params = {'page': page_num}
        
        # Preserve search and sort parameters
        if self.search_query:
            params['search'] = self.search_query
        if self.sort_field:
            params['sort'] = self.sort_field
            params['order'] = self.sort_order
        
        return url_for(request.endpoint, **params)
    
    def get_sort_icon(self, field_name: str) -> str:
        """
        Get sort icon for a field header.
        
        Args:
            field_name: Name of field
            
        Returns:
            Bootstrap icon class
        """
        if self.sort_field != field_name:
            return 'bi-arrow-down-up'
        
        if self.sort_order == 'asc':
            return 'bi-arrow-up'
        else:
            return 'bi-arrow-down'
    
    def format_cell_value(self, record, field: Field) -> str:
        """
        Format a cell value for display.
        
        Args:
            record: Database record
            field: Field definition
            
        Returns:
            Formatted string value
        """
        value = getattr(record, field.name, None)
        
        if value is None:
            return ''
        
        # Use field's format_value method
        formatted = field.format_value(value)
        
        # Truncate long text for mobile
        if len(formatted) > 50:
            return formatted[:47] + '...'
        
        return formatted
    
    def export_csv(self) -> Response:
        """
        Export list data as CSV file.
        
        Returns:
            Flask Response with CSV data
        """
        # Process request parameters (but ignore pagination for export)
        self.process_request_params()
        
        # Get all matching records (no pagination)
        query = self.get_query()
        records = query.all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header row
        headers = []
        for field in self.display_fields:
            header = field.name.replace('_', ' ').title()
            if field.is_lookup_field() and field.name.endswith('_id'):
                # Clean up lookup field names for display
                header = field.name[:-3].replace('_', ' ').title()
            headers.append(header)
        
        # Add system fields
        headers.extend(['ID', 'Created At', 'Updated At'])
        writer.writerow(headers)
        
        # Write data rows
        for record in records:
            row = []
            
            # Field values
            for field in self.display_fields:
                value = getattr(record, field.name, None)
                
                # Handle lookup fields - get display value
                if field.is_lookup_field() and value:
                    # Try to get the related record and display field
                    try:
                        if hasattr(self.table, 'db') and self.table.db:
                            lookup_model = field._get_lookup_model(self.table.db)
                            if lookup_model:
                                lookup_record = self.table.db.session.query(lookup_model).filter_by(id=value).first()
                                if lookup_record:
                                    display_value = getattr(lookup_record, field.display, str(value))
                                    value = display_value
                    except Exception:
                        # If lookup fails, just use the raw value
                        pass
                
                # Format the value
                if value is not None:
                    formatted_value = field.format_value(value)
                    # Remove HTML tags and clean up for CSV
                    formatted_value = str(formatted_value).replace('\n', ' ').replace('\r', '')
                    row.append(formatted_value)
                else:
                    row.append('')
            
            # System fields
            row.append(getattr(record, 'id', ''))
            
            created_at = getattr(record, 'created_at', None)
            if created_at:
                row.append(created_at.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                row.append('')
            
            updated_at = getattr(record, 'updated_at', None)
            if updated_at:
                row.append(updated_at.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                row.append('')
            
            writer.writerow(row)
        
        # Create response
        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        
        # Create filename
        filename = f"{self.table.name}.csv"
        
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
        return response
    
    def render(self, template_name: str = None, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Render the list view.
        
        Args:
            template_name: Optional custom template name
            filters: Optional dictionary of field_name -> value filters
            
        Returns:
            Rendered HTML
        """
        # Process request parameters
        self.process_request_params()
        
        # Get paginated results
        pagination = self.get_paginated_results(filters)
        
        # Use proper template that extends base.html
        template = template_name or 'crud/list.html'
        return render_template(template, 
                             listview=self, 
                             pagination=pagination)
    
    def _render_default_list(self, pagination) -> str:
        """Render the default mobile-first list template."""
        
        # Build search form
        search_form = f'''
        <form method="GET" class="mb-3" data-search>
            <div class="input-group">
                <input type="search" 
                       name="search" 
                       class="form-control" 
                       placeholder="Search {self.table.name}..." 
                       value="{self.search_query}"
                       aria-label="Search">
                <button type="submit" class="btn btn-outline-secondary">
                    <i class="bi bi-search"></i>
                </button>
            </div>
            {f'<input type="hidden" name="sort" value="{self.sort_field}">' if self.sort_field else ''}
            {f'<input type="hidden" name="order" value="{self.sort_order}">' if self.sort_field else ''}
        </form>
        '''
        
        # Build mobile-optimized table/cards
        records_html = []
        
        for record in pagination.items:
            # Mobile card view
            card_fields = []
            for field in self.display_fields[:3]:  # Show top 3 fields in cards
                value = self.format_cell_value(record, field)
                if value:
                    card_fields.append(f'''
                    <div class="d-flex justify-content-between">
                        <span class="text-muted">{field.name.replace('_', ' ').title()}:</span>
                        <span>{value}</span>
                    </div>
                    ''')
            
            record_html = f'''
            <div class="card mb-2 d-md-none">
                <div class="card-body py-2">
                    {''.join(card_fields)}
                    <div class="mt-2">
                        <a href="{record.id}/" class="btn btn-sm btn-outline-primary me-1">
                            <i class="bi bi-eye"></i> View
                        </a>
                        <a href="{record.id}/edit" class="btn btn-sm btn-outline-secondary">
                            <i class="bi bi-pencil"></i> Edit
                        </a>
                    </div>
                </div>
            </div>
            '''
            records_html.append(record_html)
        
        # Build desktop table
        table_headers = []
        for field in self.display_fields:
            sort_icon = self.get_sort_icon(field.name)
            sort_url = self.get_sort_url(field.name)
            
            table_headers.append(f'''
            <th scope="col">
                <a href="{sort_url}" class="text-decoration-none text-reset">
                    {field.name.replace('_', ' ').title()}
                    <i class="bi {sort_icon} ms-1"></i>
                </a>
            </th>
            ''')
        
        table_rows = []
        for record in pagination.items:
            cells = []
            for field in self.display_fields:
                value = self.format_cell_value(record, field)
                cells.append(f'<td>{value}</td>')
            
            table_rows.append(f'''
            <tr>
                {''.join(cells)}
                <td>
                    <div class="btn-group btn-group-sm">
                        <a href="{record.id}/" class="btn btn-outline-primary">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="{record.id}/edit" class="btn btn-outline-secondary">
                            <i class="bi bi-pencil"></i>
                        </a>
                    </div>
                </td>
            </tr>
            ''')
        
        desktop_table = f'''
        <div class="table-responsive d-none d-md-block">
            <table class="table table-hover">
                <thead class="table-light">
                    <tr>
                        {''.join(table_headers)}
                        <th scope="col" width="120">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
        </div>
        '''
        
        # Build pagination
        pagination_html = self._build_pagination(pagination)
        
        # Complete template
        template = f'''
        <div class="container-fluid">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h1 class="h3 mb-0">{self.table.name.title()}</h1>
                <a href="new" class="btn btn-primary">
                    <i class="bi bi-plus-lg me-1"></i>Add New
                </a>
            </div>
            
            {search_form}
            
            <!-- Mobile cards -->
            {''.join(records_html)}
            
            <!-- Desktop table -->
            {desktop_table}
            
            {pagination_html}
            
            {f'<div class="text-center text-muted mt-3">No {self.table.name} found.</div>' if not pagination.items else ''}
        </div>
        
        <style>
        /* Mobile-first optimizations */
        @media (max-width: 767px) {{
            .btn-group-sm .btn {{
                padding: 0.25rem 0.5rem;
                font-size: 0.875rem;
            }}
        }}
        
        /* Card hover effects */
        .card:hover {{
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            transform: translateY(-1px);
            transition: all 0.2s ease-in-out;
        }}
        
        /* Table sorting */
        th a:hover {{
            background-color: rgba(0, 0, 0, 0.05);
        }}
        </style>
        '''
        
        return template
    
    def _build_pagination(self, pagination) -> str:
        """Build pagination HTML."""
        if pagination.pages <= 1:
            return ''
        
        pages = []
        
        # Previous button
        if pagination.has_prev:
            prev_url = self.get_page_url(pagination.prev_num)
            pages.append(f'''
            <li class="page-item">
                <a class="page-link" href="{prev_url}">
                    <i class="bi bi-chevron-left"></i>
                </a>
            </li>
            ''')
        else:
            pages.append('<li class="page-item disabled"><span class="page-link"><i class="bi bi-chevron-left"></i></span></li>')
        
        # Page numbers (show max 5 pages)
        start_page = max(1, pagination.page - 2)
        end_page = min(pagination.pages + 1, start_page + 5)
        
        for page_num in range(start_page, end_page):
            if page_num == pagination.page:
                pages.append(f'<li class="page-item active"><span class="page-link">{page_num}</span></li>')
            else:
                page_url = self.get_page_url(page_num)
                pages.append(f'<li class="page-item"><a class="page-link" href="{page_url}">{page_num}</a></li>')
        
        # Next button
        if pagination.has_next:
            next_url = self.get_page_url(pagination.next_num)
            pages.append(f'''
            <li class="page-item">
                <a class="page-link" href="{next_url}">
                    <i class="bi bi-chevron-right"></i>
                </a>
            </li>
            ''')
        else:
            pages.append('<li class="page-item disabled"><span class="page-link"><i class="bi bi-chevron-right"></i></span></li>')
        
        return f'''
        <nav aria-label="Page navigation">
            <ul class="pagination pagination-sm justify-content-center">
                {''.join(pages)}
            </ul>
            <div class="text-center text-muted small mt-2">
                Showing {pagination.per_page * (pagination.page - 1) + 1} to {min(pagination.per_page * pagination.page, pagination.total)} of {pagination.total} entries
            </div>
        </nav>
        '''
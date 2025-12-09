function renderProductTable(products) {
  // Ensure Underscore is available
  if (typeof _ === 'undefined') {
    return 'Error: Underscore.js (_) is not loaded.';
  }

  const templateStr = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
      <table style="width: 100%; border-collapse: collapse; background: white;">
        <thead>
          <tr style="background-color: #f8fafc; text-align: left;">
            <th style="padding: 12px 16px; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Ref</th>
            <th style="padding: 12px 16px; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Name</th>
            <th style="padding: 12px 16px; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Type</th>
            <th style="padding: 12px 16px; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Unit</th>
            <th style="padding: 12px 16px; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; text-align: right;">Qty</th>
            <th style="padding: 12px 16px; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; text-align: right;">Price</th>
          </tr>
        </thead>
        <tbody>
          <% _.each(items, function(item) { 
              /* --- LOGIC PREP --- */
              var uom = (item.uom_id && item.uom_id.length === 2) ? item.uom_id[1] : '-';
              var isService = item.type === 'service';
              var price = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(item.list_price);
              var badgeColor = isService ? '#fff7ed' : '#f0fdf4'; /* Orange-ish for service, Green-ish for product */
              var badgeText = isService ? '#c2410c' : '#15803d';
          %>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 12px 16px; color: #334155; font-weight: 600; font-size: 0.9rem;">
              <%= item.default_code || '' %>
            </td>
            <td style="padding: 12px 16px; color: #0f172a; font-size: 0.95rem;">
              <%= item.name %>
            </td>
            <td style="padding: 12px 16px;">
              <span style="background-color: <%= badgeColor %>; color: <%= badgeText %>; padding: 4px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
                <%= item.type %>
              </span>
            </td>
            <td style="padding: 12px 16px; color: #64748b; font-size: 0.9rem;">
              <%= uom %>
            </td>
            <td style="padding: 12px 16px; text-align: right; color: #334155; font-family: monospace;">
              <%= isService ? '-' : item.qty_available %>
            </td>
            <td style="padding: 12px 16px; text-align: right; font-weight: bold; color: #0f172a; font-family: monospace;">
              <%= price %>
            </td>
          </tr>
          <% }); %>
        </tbody>
      </table>
    </div>
  `;

  // Compile and run
  var compiled = _.template(templateStr);
  return compiled({ items: products });
}

function renderDynamicTable(data) {
    if (!data || !Array.isArray(data) || data.length === 0) {
        return '<div style="padding: 20px; color: #666; font-family: sans-serif;">No data available to display.</div>';
    }

    // 1. Extract Headers dynamically from the first object
    const headers = Object.keys(data[0]);

    // 2. Define the Helper Logic for Smart Formatting
    // We pass this into the template so it can use it during the render loop
    const formatValue = (key, value) => {
        // Handle Nulls
        if (value === null || value === undefined) return '<span style="color: #ccc;">-</span>';

        // Handle Booleans (Visual Badge)
        if (typeof value === 'boolean') {
            const color = value ? '#dcfce7' : '#fee2e2';
            const text = value ? '#166534' : '#991b1b';
            const label = value ? 'Yes' : 'No';
            return `<span style="background:${color}; color:${text}; padding:2px 8px; border-radius:10px; font-size:0.75em; font-weight:bold;">${label}</span>`;
        }

        // Handle Arrays
        if (Array.isArray(value)) {
            // Odoo M2O Pattern Detection: [Integer, String]
            if (value.length === 2 && typeof value[0] === 'number' && typeof value[1] === 'string') {
                return `<a href="#" style="color: #4f46e5; text-decoration: none; border-bottom: 1px dashed #4f46e5;">${value[1]}</a>`;
            }
            // Standard List
            return value.join(', ');
        }

        // Handle Numbers (Currency Detection)
        if (typeof value === 'number') {
            const lowerKey = key.toLowerCase();
            if (lowerKey.includes('price') || lowerKey.includes('amount') || lowerKey.includes('total') || lowerKey.includes('cost')) {
                return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
            }
            return value;
        }

        // Handle Complex Objects
        if (typeof value === 'object') {
            return `<code style="background:#f1f5f9; padding:2px 4px; border-radius:4px; font-size:0.8em; color:#475569;">${JSON.stringify(value).slice(0, 30)}...</code>`;
        }

        return String(value);
    };

    // 3. The Underscore Template
    const templateStr = `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
                border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; background: white; font-size: 0.9rem;">
                <thead>
                    <tr style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                        <% _.each(headers, function(header) { %>
                            <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #475569; 
                                       text-transform: capitalize; white-space: nowrap;">
                                <%= header.replace(/_/g, ' ') %>
                            </th>
                        <% }); %>
                    </tr>
                </thead>
                <tbody>
                    <% _.each(items, function(row, index) { %>
                        <tr style="border-bottom: 1px solid #f1f5f9; background-color: <%= index % 2 === 0 ? '#ffffff' : '#fcfcfc' %>;">
                            <% _.each(headers, function(key) { %>
                                <td style="padding: 10px 16px; color: #334155; vertical-align: middle;">
                                    <%= formatter(key, row[key]) %>
                                </td>
                            <% }); %>
                        </tr>
                    <% }); %>
                </tbody>
            </table>
        </div>
        <div style="background: #f8fafc; padding: 8px 16px; text-align: right; color: #94a3b8; font-size: 0.75rem; border-top: 1px solid #e2e8f0;">
            <%= items.length %> records found
        </div>
    </div>
    `;

    // 4. Compile and Execute
    const compiled = _.template(templateStr);
    return compiled({ 
        items: data, 
        headers: headers, 
        formatter: formatValue 
    });
}

/**
 * Renders JSON into a "Dark Mode / Terminal" styled HTML table.
 * Matches the M8P interface: Monospace font, Orange accents, Dark grid.
 */
function renderTerminalTable(data) {
    if (!data || !Array.isArray(data) || data.length === 0) {
        return '<div style="font-family: monospace; color: #666; padding: 10px;">> NO_DATA_FOUND</div>';
    }

    // 1. Extract Headers
    const headers = Object.keys(data[0]);

    // 2. Formatter Logic (Adapted for Dark Theme)
    const formatValue = (key, value) => {
        if (value === null || value === undefined) return '<span style="color: #444;">null</span>';

        // Booleans: Terminal style [YES] / [NO]
        if (typeof value === 'boolean') {
            const color = value ? '#00ff41' : '#ff3333'; // Neon Green / Red
            return `<span style="color:${color}; font-weight:bold;">[${value ? 'TRUE' : 'FALSE'}]</span>`;
        }

        // Arrays (M2O or Lists)
        if (Array.isArray(value)) {
            if (value.length === 2 && typeof value[0] === 'number') {
                // Link style for Odoo relations
                return `<span style="color: #ff9f43; text-decoration: underline; cursor: pointer;">${value[1]}</span>`;
            }
            return `[${value.join(', ')}]`;
        }

        // Currency / Numbers
        if (typeof value === 'number') {
            const lowerKey = key.toLowerCase();
            // Check for money fields
            if (lowerKey.includes('price') || lowerKey.includes('amount') || lowerKey.includes('total')) {
                return `<span style="color: #2ecc71;">${new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)}</span>`;
            }
            // Standard numbers
            return `<span style="color: #3498db;">${value}</span>`;
        }

        return String(value);
    };

    // 3. The "M8P" Terminal Template
    const templateStr = `
    <div style="
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace; 
        background-color: #0d0d0d; 
        border: 1px solid #333; 
        color: #e0e0e0;
        font-size: 13px;
        margin-top: 10px;
    ">
        <div style="
            background-color: #1a1a1a; 
            padding: 4px 8px; 
            border-bottom: 1px solid #333;
            color: #ff5722; 
            font-size: 11px;
            letter-spacing: 1px;
        ">
            >> DATA_OUTPUT_STREAM [${data.length}]
        </div>

        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 1px solid #ff5722;"> <% _.each(headers, function(header) { %>
                            <th style="
                                text-align: left; 
                                padding: 8px 12px; 
                                color: #ff5722; /* Orange Headers */
                                text-transform: uppercase; 
                                font-weight: normal;
                                border-right: 1px solid #222;
                            ">
                                <%= header %>
                            </th>
                        <% }); %>
                    </tr>
                </thead>
                <tbody>
                    <% _.each(items, function(row, index) { %>
                        <tr style="border-bottom: 1px solid #222;">
                            <% _.each(headers, function(key) { %>
                                <td style="
                                    padding: 8px 12px; 
                                    border-right: 1px solid #222;
                                    color: #ccc;
                                ">
                                    <%= formatter(key, row[key]) %>
                                </td>
                            <% }); %>
                        </tr>
                    <% }); %>
                </tbody>
            </table>
        </div>
        <div style="padding: 4px 8px; font-size: 10px; color: #555; text-align: right;">
            END_OF_STREAM // ${(new Date()).toISOString()}
        </div>
    </div>
    `;

    // 4. Compile
    if (typeof _ === 'undefined') return "Error: Underscore.js missing";
    
    const compiled = _.template(templateStr);
    return compiled({ 
        items: data, 
        headers: headers, 
        formatter: formatValue 
    });
}
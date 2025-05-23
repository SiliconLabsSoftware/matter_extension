local changeset = {}

if slc.is_selected('matter_gatt') then
  table.insert(changeset, {
    ['component'] = '%extension-matter%matter_gatt',
    ['action'] = 'remove',
  })

  if slc.is_selected('matter_zigbee_multiprotocol_common') then
    table.insert(changeset, {
      ['component'] = '%extension-matter%matter_ble_side_channel',
      ['action'] = 'add'
    })
  else
    table.insert(changeset, {
      ['component'] = '%extension-matter%matter_gatt_static',
      ['action'] = 'add'
    })
  end
end

return changeset
local changeset = {}

-- Enable the use of CTM and the static secure token size for Series 3 devices
if slc.is_provided("matter_provision_default") and slc.is_provided("device_series_3") then
  slc.component("matter_use_ctm"):select()
end

return changeset

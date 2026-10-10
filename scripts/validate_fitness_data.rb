#!/usr/bin/env ruby
# Validate the cross-file records used by the workout feedback loop.

require 'csv'
require 'date'
require 'digest'
require 'json'
require 'yaml'

root = File.expand_path('..', __dir__)
csv_path = File.join(root, 'data/logs/structured/sessions.csv')
yaml_path = File.join(root, 'data/logs/structured/sessions.yaml')
manifest = JSON.parse(File.read(File.join(root, 'data/menus/prescriptions.json')))
trials = JSON.parse(File.read(File.join(root, 'data/menus/active-trials.json')))
menu_text = File.read(File.join(root, 'data/menus/current-menus.md'))
baseline_menu_text = menu_text.gsub(/^## 次回[^\n]*\n.*?(?=^## |^# |\z)/m, '')
quick_text = File.read(File.join(root, 'README.md'))
sessions = YAML.safe_load(File.read(yaml_path), [Date], [], true).fetch('sessions')
rows = CSV.read(csv_path, headers: true)
errors = []

# Review results are mutable state, with stable IDs shared by decisions and tasks.
review_entries = {}
{
  'current-assessment.md' => ['J', %w[keep hold change]],
  'backlog.md' => ['B', %w[open waiting resolved]]
}.each do |name, (prefix, statuses)|
  path = File.join(root, 'data/logs/reviews', name)
  unless File.file?(path)
    errors << "missing review SSOT: #{name}"
    next
  end
  text = File.read(path)
  blocks = text.scan(/^## (#{prefix}-\d{3,})：[^\n]+\n(.*?)(?=^## |\z)/m)
  errors << "no review entries: #{name}" if blocks.empty?
  ids = blocks.map(&:first)
  errors << "duplicate review id: #{name}" unless ids.uniq.length == ids.length
  review_entries[prefix] = blocks.to_h
  dates = text.scan(/^- updated_on: (.*)$/).flatten
  errors << "missing review update date: #{name}" if dates.empty?
  dates.each do |value|
    begin
      Date.iso8601(value)
    rescue ArgumentError
      errors << "invalid review update date: #{name} #{value}"
    end
  end
  blocks.each do |id, body|
    status = body[/^- status: (.*)$/, 1]
    errors << "invalid review status: #{id}" unless statuses.include?(status)
    errors << "missing review update date: #{id}" unless body.match?(/^- updated_on: /)
    if prefix == 'J'
      %w[判断 再検討条件].each do |field|
        errors << "missing review #{field}: #{id}" unless body.match?(/\*\*#{field}\*\*：\S/)
      end
    else
      errors << "invalid backlog priority: #{id}" unless body.match?(/^- priority: P[123]$/)
      %w[問い 現状 次の確認 解決条件].each do |field|
        errors << "missing backlog #{field}: #{id}" unless body.match?(/\*\*#{field}\*\*：\S/)
      end
      if status == 'resolved' && !body.match?(/\*\*解決結果\*\*：\S/)
        errors << "resolved backlog lacks outcome: #{id}"
      end
    end
  end
end
review_entries.fetch('B', {}).each do |id, body|
  refs = body[/^- decisions: (.*)$/, 1].to_s.split(/,\s*/)
  if refs.empty? || refs.any? { |ref| !review_entries.fetch('J', {}).key?(ref) }
    errors << "unknown or missing judgment reference: #{id}"
  end
end
review_entries.fetch('J', {}).each do |id, body|
  body.scan(/\bB-\d{3,}\b/).each do |ref|
    errors << "unknown backlog reference: #{id} #{ref}" unless review_entries.fetch('B', {}).key?(ref)
  end
end
request_state_path = File.join(root, 'data/logs/reviews/review-request-state.json')
if File.file?(request_state_path)
  state = JSON.parse(File.read(request_state_path))
  errors << 'invalid latest request date' unless state['requested_at'].is_a?(String) && state['requested_at'].match?(/\A\d{4}-\d{2}-\d{2}/)
  Array(state['files_used']).each do |path|
    errors << "missing review request source: #{path}" unless File.file?(File.join(root, path))
  end
  if state['prompt_file'] && !File.file?(File.expand_path(state['prompt_file'], root))
    errors << 'missing latest review request'
  end
else
  errors << 'missing latest review request state'
end

key = ->(row) { [row.fetch('date').to_s, row.fetch('session_type')] }
csv_keys = rows.map { |row| key.call(row) }
yaml_keys = sessions.map { |row| key.call(row) }
errors << 'duplicate CSV session' if csv_keys.uniq.length != csv_keys.length
errors << 'duplicate YAML session' if yaml_keys.uniq.length != yaml_keys.length
errors << 'CSV/YAML session mismatch' unless csv_keys.sort == yaml_keys.sort
review_entries.each_value do |entries|
  entries.each do |id, body|
    body.scan(/`(\d{4}-\d{2}-\d{2} [ABC]_\w+)`/).flatten.each do |ref|
      errors << "unknown review session reference: #{id} #{ref}" unless yaml_keys.include?(ref.split(' ', 2))
    end
  end
end

snapshots = manifest.fetch('snapshots')
snapshot_ids = snapshots.map { |item| item.fetch('id') }
errors << 'duplicate prescription id' if snapshot_ids.uniq.length != snapshot_ids.length
current = snapshots.find { |item| item.fetch('id') == manifest.fetch('current_id') }
if current.nil?
  errors << 'current prescription missing'
else
  errors << 'current menu baseline hash mismatch' unless Digest::SHA256.hexdigest(baseline_menu_text) == current.fetch('source_sha256')
end

trial_ids = trials.fetch('trials').map { |item| item.fetch('id') }
errors << 'duplicate trial id' if trial_ids.uniq.length != trial_ids.length
machine_titles = {
  'lat_pulldown' => 'Lat Pulldown', 'row_machine' => 'Row Machine',
  'chest_press' => 'Chest Press', 'shoulder_press' => 'Shoulder Press'
}
active_counts = trials.fetch('trials').select { |item| item['status'] == 'active' }.group_by { |item| item['menu'] }
errors << 'multiple active trials for a menu' if active_counts.any? { |_menu, items| items.length > 1 }
trials.fetch('trials').each do |trial|
  errors << "missing source session for trial #{trial['id']}" unless yaml_keys.include?(trial.fetch('source_session').split(' ', 2))
  if trial['source_review'] && !File.file?(File.join(root, trial['source_review']))
    errors << "missing review reference for trial #{trial['id']}"
  end
  if trial['status'] == 'active'
    subsequent = csv_keys.find do |session_date, session_type|
      session_date > trial.fetch('created_on') && session_type.start_with?("#{trial.fetch('menu')}_")
    end
    errors << "active trial not closed after #{subsequent[0]}: #{trial['id']}" if subsequent
    if current
      baseline = current.fetch('menus').fetch(trial.fetch('menu'))
      trial.fetch('targets').each do |target|
        title = machine_titles[target['exercise_id']]
        next unless title && target.fetch('fields').key?('weight_kg')
        planned = baseline.find { |exercise| exercise['id'] == target['exercise_id'] }
        errors << "trial target missing from baseline: #{target['exercise_id']}" unless planned
        next unless planned
        from = planned.fetch('weight_kg')
        to = target.fetch('fields').fetch('weight_kg')
        errors << "trial missing from current menu: #{trial['id']} #{title}" unless menu_text.include?("#{title}: #{from}kg → **#{to}kg**")
        errors << "trial missing from Quick Reference: #{trial['id']} #{title}" unless quick_text.include?("#{title}: **#{to}kg**")
      end
    end
  end
end

sessions.each do |session|
  prescription_id = session['prescription_id']
  next unless prescription_id

  snapshot = snapshots.find { |item| item['id'] == prescription_id }
  if snapshot.nil?
    errors << "unknown prescription for #{key.call(session).join(' ')}"
    next
  end
  date = Date.parse(session.fetch('date').to_s)
  errors << "future prescription for #{date}" if Date.parse(snapshot.fetch('effective_from')) > date
  csv_row = rows.find { |row| key.call(row) == key.call(session) }
  if csv_row
    %w[duration_min avg_hr max_hr aerobic_te anaerobic_te exercise_load calories].each do |field|
      next unless session.key?(field)
      errors << "CSV/YAML #{field} mismatch for #{date}" unless (csv_row[field].to_f - session[field].to_f).abs < 0.011
    end
    %w[zone1_time zone2_time zone3_time zone4_time zone5_time primary_benefit].each do |field|
      errors << "CSV/YAML #{field} mismatch for #{date}" unless csv_row[field] == session[field]
    end
  end
  menu = session.fetch('session_type')[0]
  exercises = snapshot.fetch('menus').fetch(menu)
  weights = exercises.select { |item| item['kind'] == 'machine' }.to_h { |item| [item['id'], item['weight_kg']] }
  prescribed = session.dig('prescribed_workout', 'machine_weights_kg')
  if prescribed
    errors << "prescribed weights mismatch for #{date}" unless prescribed == weights
    planned_sets = exercises.select { |item| item['kind'] == 'machine' }.sum { |item| item.fetch('sets') }
    errors << "prescribed set count mismatch for #{date}" unless session.dig('prescribed_workout', 'prescribed_machine_sets') == planned_sets
  end
  effective = session.dig('effective_execution', 'machine_weights')
  if effective
    errors << "effective machine IDs mismatch for #{date}" unless effective.keys.sort == weights.keys.sort
    effective.each do |machine, detail|
      next unless detail['provenance'] == 'user_confirmed_reference_weight'
      errors << "confirmed reference weight mismatch for #{date} #{machine}" unless detail['weight_kg'] == weights[machine]
    end
  end
end

if errors.any?
  warn errors.join("\n")
  exit 1
end

puts "OK: #{rows.length} CSV/YAML sessions, #{snapshots.length} prescription snapshot, #{trial_ids.length} trials, #{review_entries.fetch('J', {}).length} judgments, #{review_entries.fetch('B', {}).length} backlog items"

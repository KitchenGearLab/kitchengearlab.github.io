# Local QA renderer using GitHub Pages' exact Liquid version. Publication uses
# GitHub's existing Jekyll build; this helper is not a deployment dependency.
gem 'liquid', '= 4.0.4'
require 'liquid'
require 'fileutils'
require 'json'
root = File.expand_path('..', __dir__)
destination = File.join(root, '_site', 'header2')
source = File.read(File.join(root, '_includes', 'header.html'), encoding: 'UTF-8')
template = Liquid::Template.parse(source, error_mode: :strict)
files = IO.popen(['git', '-C', root, 'ls-files'], &:read).lines.map(&:strip).reject do |path|
  path.split('/').any? { |part| part.start_with?('_', '.') || part == 'scripts' } || path.end_with?('-original.png') || ['Gemfile', 'Gemfile.lock'].include?(path)
end
count = 0
files.each do |path|
  original = File.join(root, path)
  next unless File.file?(original)
  target = File.join(destination, path)
  FileUtils.mkdir_p(File.dirname(target))
  if path.end_with?('index.html')
    text = File.read(original, encoding: 'UTF-8').sub(/\A---\n.*?\n---\n/m, '')
    url = '/' + path.sub(/index\.html\z/, '')
    context = {'page' => {'url' => url}, 'include' => {'part' => 'head'}}
    head = template.render!(context, strict_filters: true)
    header = template.render!({'page' => {'url' => url}, 'include' => {}}, strict_filters: true)
    text = text.sub('{% include header.html part="head" %}', head).sub('{% include header.html %}', header)
    raise "Unrendered Liquid in #{path}" if text.include?('{%') || text.include?('{{')
    File.binwrite(target, text)
    count += 1
  else
    FileUtils.copy_file(original, target)
  end
end
puts JSON.generate({liquid: Liquid::VERSION, pages: count, public_files: files.length, destination: destination})

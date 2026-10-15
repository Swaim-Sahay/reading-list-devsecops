{{- define "rl.labels" -}}
app.kubernetes.io/part-of: readinglist
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

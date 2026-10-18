import { supabase } from '../../lib/supabase.js'

export async function fetchLists() {
  const { data, error } = await supabase
    .from('personal_lists')
    .select('*, list_items(id, status, checked)')
    .order('created_at', { ascending: false })
  if (error) throw error
  return data ?? []
}

export async function fetchList(id) {
  const { data, error } = await supabase
    .from('personal_lists')
    .select('*')
    .eq('id', id)
    .single()
  if (error) throw error
  return data
}

export async function fetchListItems(listId) {
  const { data, error } = await supabase
    .from('list_items')
    .select('*')
    .eq('list_id', listId)
    .order('checked', { ascending: true })
    .order('created_at', { ascending: false })
  if (error) throw error
  return data ?? []
}

export async function createList({ name, color, icon }) {
  const { data, error } = await supabase
    .from('personal_lists')
    .insert({ name, color, icon })
    .select()
    .single()
  if (error) throw error
  return data
}

export async function deleteList(id) {
  const { error } = await supabase.from('personal_lists').delete().eq('id', id)
  if (error) throw error
}

export async function createItem({ list_id, text, note }) {
  const { data, error } = await supabase
    .from('list_items')
    .insert({ list_id, text, note })
    .select()
    .single()
  if (error) throw error
  return data
}

export async function updateItem(id, patch) {
  const { data, error } = await supabase
    .from('list_items')
    .update(patch)
    .eq('id', id)
    .select()
    .single()
  if (error) throw error
  return data
}

export async function deleteItem(id) {
  const { error } = await supabase.from('list_items').delete().eq('id', id)
  if (error) throw error
}

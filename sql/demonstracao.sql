-- Exclusivamente para base descartável. Não executar no banco de uso.
BEGIN;
INSERT INTO demands(id,title,client,stage,due,notes,created_at,updated_at)
VALUES(1,'Post de demonstração A','Referência A','Solicitado','2026-11-06','','2026-11-04T12:00:00+00:00','2026-11-04T12:00:00+00:00');
INSERT INTO demands(id,title,client,stage,due,notes,created_at,updated_at)
VALUES(2,'Post de demonstração B','Referência B','Solicitado','2026-11-07','','2026-11-04T12:00:00+00:00','2026-11-04T12:00:00+00:00');
INSERT INTO history(demand_id,previous_stage,new_stage,note,happened_at)
VALUES(1,NULL,'Solicitado','Criação','2026-11-04T12:00:00+00:00'),
      (2,NULL,'Solicitado','Criação','2026-11-04T12:00:00+00:00');
UPDATE demands SET stage='Em produção',updated_at='2026-11-04T13:00:00+00:00' WHERE id=1;
INSERT INTO history(demand_id,previous_stage,new_stage,note,happened_at)
VALUES(1,'Solicitado','Em produção','Produção iniciada','2026-11-04T13:00:00+00:00');
INSERT INTO incidents(demand_id,title,category,description,impact,action,lesson,status,created_at,updated_at)
VALUES(1,'Conferência de linguagem','Respeito e dignidade','Expressão ambígua em rascunho de teste','Possível interpretação inadequada','','','Aberto','2026-11-04T13:00:00+00:00','2026-11-04T13:00:00+00:00'),
      (NULL,'Revisão de texto assistido','Uso de IA','Revisão humana de texto demonstrativo','Possibilidade de informação sem confirmação','','','Aberto','2026-11-04T13:00:00+00:00','2026-11-04T13:00:00+00:00');
UPDATE incidents SET status='Encerrado',action='Reformular a expressão',lesson='Revisar clareza antes do envio',updated_at='2026-11-04T14:00:00+00:00' WHERE id=1;
INSERT INTO demands(id,title,client,stage,due,notes,created_at,updated_at)
VALUES(99,'Registro descartável','Referência de teste','Cancelado','2026-11-08','','2026-11-04T12:00:00+00:00','2026-11-04T12:00:00+00:00');
SELECT COUNT(*) AS descartavel_antes FROM demands WHERE id=99;
DELETE FROM demands WHERE id=99;
SELECT COUNT(*) AS descartavel_depois FROM demands WHERE id=99;
COMMIT;
SELECT id,title,stage,due FROM demands ORDER BY due,id;
SELECT i.id,i.status,COALESCE(d.title,'Sem demanda') AS demanda
FROM incidents i LEFT JOIN demands d ON d.id=i.demand_id ORDER BY i.id;
SELECT stage,COUNT(*) AS quantidade FROM demands GROUP BY stage ORDER BY stage;
SELECT demand_id,previous_stage,new_stage,happened_at FROM history WHERE demand_id=1 ORDER BY id;
SELECT id,title,due FROM demands WHERE stage NOT IN ('Publicado','Cancelado') AND due <= '2026-11-06' ORDER BY due,id;
PRAGMA foreign_key_check;
PRAGMA integrity_check;
